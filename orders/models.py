from django.db import models
from django.core.validators import MinValueValidator

from menu.models import MenuItem


class Order(models.Model):
    """A customer's submitted restaurant order."""

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        CONFIRMED = 'confirmed', 'Confirmed'
        PREPARING = 'preparing', 'Preparing'
        SERVED = 'served', 'Served'
        CANCELLED = 'cancelled', 'Cancelled'

    customer_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    table_number = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)]
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f'Order #{self.pk} - Table {self.table_number}'


class OrderItem(models.Model):
    """A price snapshot of one menu item in an order."""

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
    )
    menu_item = models.ForeignKey(
        MenuItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='order_items',
    )
    item_name = models.CharField(max_length=100)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    @property
    def line_total(self):
        return self.unit_price * self.quantity

    def __str__(self):
        return f'{self.quantity} × {self.item_name} (Order #{self.order_id})'
