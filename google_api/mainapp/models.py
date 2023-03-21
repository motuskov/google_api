from django.db import models

class OrderItem(models.Model):
    '''Represents an item of an order.
    '''
    order_number = models.PositiveIntegerField(
        help_text='Number of the order that contains the item.'
    )
    cost_usd = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        help_text='The cost of the item in US dollars.'
    )
    cost_rub = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        help_text='The cost of the item in Russian rubles.'
    )
    delivery_time = models.DateField(
        help_text='The date by which the item must be delivered.'
    )
