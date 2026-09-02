from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from menu.models import MenuItem
from .models import Order, OrderItem


class OrderingFlowTests(TestCase):
    def setUp(self):
        self.paneer = MenuItem.objects.create(
            name='Paneer Tikka',
            description='Grilled paneer with aromatic spices.',
            price=Decimal('180.00'),
            category='Starters',
        )

    def _set_customer_name(self):
        session = self.client.session
        session['customer_name'] = 'Rani'
        session.save()

    def test_home_saves_customer_name_in_session(self):
        response = self.client.post(reverse('home'), {'name': 'Rani'})

        self.assertRedirects(response, reverse('menu'))
        self.assertEqual(self.client.session['customer_name'], 'Rani')

    def test_add_to_cart_stores_quantity_in_session(self):
        response = self.client.post(reverse('add_to_cart', args=[self.paneer.id]))

        self.assertRedirects(response, reverse('menu'))
        self.assertEqual(self.client.session['cart'], {str(self.paneer.id): 1})

    def test_checkout_creates_an_order_and_price_snapshot(self):
        self._set_customer_name()
        self.client.post(reverse('add_to_cart', args=[self.paneer.id]))

        response = self.client.post(reverse('place_order'), {
            'phone_number': '9876543210',
            'table_number': '4',
        })

        self.assertRedirects(response, reverse('order_confirmation'))
        order = Order.objects.get()
        item = OrderItem.objects.get()
        self.assertEqual(order.customer_name, 'Rani')
        self.assertEqual(order.table_number, 4)
        self.assertEqual(order.total_amount, Decimal('180.00'))
        self.assertEqual(item.menu_item, self.paneer)
        self.assertEqual(item.item_name, 'Paneer Tikka')
        self.assertEqual(item.unit_price, Decimal('180.00'))
        self.assertEqual(item.quantity, 1)
        self.assertEqual(self.client.session['cart'], {})

    def test_checkout_rejects_an_invalid_phone_number(self):
        self._set_customer_name()
        self.client.post(reverse('add_to_cart', args=[self.paneer.id]))

        response = self.client.post(reverse('place_order'), {
            'phone_number': '123',
            'table_number': '4',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Enter a valid 10-digit Indian mobile number.')
        self.assertFalse(Order.objects.exists())
