from rest_framework import serializers

from .models import OrderItem

class OrderItemSerializer(serializers.ModelSerializer):
    '''Represents a serializer for "OrderItem" model.
    '''
    class Meta:
        model = OrderItem
        fields = (
            'id',
            'order_number',
            'cost_usd',
            'cost_rub',
            'delivery_date',
        )
