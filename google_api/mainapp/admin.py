from django.contrib import admin

from .models import OrderItem

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    '''Represents an item of an order in the administration interface.
    '''
    list_display = [
        'pk',
        'order_number',
        'cost_usd',
        'cost_rub',
        'delivery_date',
    ]
