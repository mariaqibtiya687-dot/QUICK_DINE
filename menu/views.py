from decimal import Decimal

from django.contrib import messages
from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from orders.forms import CheckoutForm, CustomerNameForm
from orders.models import Order, OrderItem
from .models import MenuItem


def _cart_quantities(request):
    """Return a clean ``{menu_item_id: quantity}`` mapping from the session."""
    cart = request.session.get('cart', {})
    if not isinstance(cart, dict):
        return {}

    quantities = {}
    for item_id, quantity in cart.items():
        try:
            item_id = int(item_id)
            quantity = int(quantity)
        except (TypeError, ValueError):
            continue
        if item_id > 0 and quantity > 0:
            quantities[item_id] = min(quantity, 20)
    return quantities


def _cart_lines(request):
    quantities = _cart_quantities(request)
    foods = MenuItem.objects.filter(
        id__in=quantities,
        is_available=True,
    )
    foods_by_id = {food.id: food for food in foods}

    lines = []
    total = Decimal('0.00')
    for item_id, quantity in quantities.items():
        food = foods_by_id.get(item_id)
        if food is None:
            continue
        line_total = food.price * quantity
        lines.append({
            'food': food,
            'quantity': quantity,
            'line_total': line_total,
        })
        total += line_total
    return lines, total


def _save_cart(request, quantities):
    request.session['cart'] = {
        str(item_id): quantity for item_id, quantity in quantities.items()
    }
    request.session.modified = True


def home(request):
    form = CustomerNameForm(initial={'name': request.session.get('customer_name', '')})
    if request.method == 'POST':
        form = CustomerNameForm(request.POST)
        if form.is_valid():
            request.session['customer_name'] = form.cleaned_data['name']
            messages.success(request, f"Welcome to Quick Dine, {form.cleaned_data['name']}!")
            return redirect('menu')

    return render(request, 'menu/home.html', {'name_form': form})


def menu(request):
    categories = MenuItem.objects.filter(is_available=True).order_by('category').values_list('category', flat=True).distinct()
    food_items = MenuItem.objects.filter(is_available=True).order_by('category', 'name')
    selected_category = request.GET.get('category', '')
    if selected_category:
        food_items = food_items.filter(category=selected_category)

    return render(request, 'menu/menu.html', {
        'categories': categories,
        'food_items': food_items,
        'selected_category': selected_category,
        'cart_count': sum(_cart_quantities(request).values()),
    })


def cart(request):
    lines, total = _cart_lines(request)
    return render(request, 'menu/cart.html', {
        'cart_lines': lines,
        'total': total,
        'checkout_form': CheckoutForm(),
        'customer_name': request.session.get('customer_name'),
    })


def order_confirmation(request):
    order_id = request.session.get('last_order_id')
    if not order_id:
        return redirect('cart')
    order = get_object_or_404(Order.objects.prefetch_related('items'), pk=order_id)
    return render(request, 'menu/order_confirmation.html', {'order': order})


@require_POST
def add_to_cart(request, item_id):
    food = get_object_or_404(MenuItem, pk=item_id, is_available=True)
    quantities = _cart_quantities(request)
    quantities[food.id] = min(quantities.get(food.id, 0) + 1, 20)
    _save_cart(request, quantities)
    messages.success(request, f'{food.name} was added to your cart.')
    return redirect('menu')


@require_POST
def update_cart(request, item_id):
    quantities = _cart_quantities(request)
    if item_id not in quantities:
        raise Http404('This item is not in your cart.')

    if request.POST.get('action') == 'remove':
        quantities.pop(item_id, None)
        messages.info(request, 'Item removed from your cart.')
    else:
        try:
            quantity = int(request.POST.get('quantity', 1))
        except (TypeError, ValueError):
            quantity = 1
        if quantity <= 0:
            quantities.pop(item_id, None)
        else:
            quantities[item_id] = min(quantity, 20)
        messages.success(request, 'Cart updated.')

    _save_cart(request, quantities)
    return redirect('cart')


@require_POST
def place_order(request):
    customer_name = request.session.get('customer_name')
    if not customer_name:
        messages.warning(request, 'Please enter your name before placing an order.')
        return redirect('home')

    lines, total = _cart_lines(request)
    if not lines:
        messages.warning(request, 'Your cart is empty. Add food before placing an order.')
        return redirect('menu')

    form = CheckoutForm(request.POST)
    if not form.is_valid():
        return render(request, 'menu/cart.html', {
            'cart_lines': lines,
            'total': total,
            'checkout_form': form,
            'customer_name': customer_name,
        })

    with transaction.atomic():
        order = Order.objects.create(
            customer_name=customer_name,
            phone_number=form.cleaned_data['phone_number'],
            table_number=form.cleaned_data['table_number'],
            total_amount=total,
        )
        OrderItem.objects.bulk_create([
            OrderItem(
                order=order,
                menu_item=line['food'],
                item_name=line['food'].name,
                unit_price=line['food'].price,
                quantity=line['quantity'],
            )
            for line in lines
        ])

    _save_cart(request, {})
    request.session['last_order_id'] = order.id
    request.session.modified = True
    return redirect('order_confirmation')
