from rest_framework import generics

from .models import OrderItem
from .serializers import OrderItemSerializer

class OrderItemList(generics.ListAPIView):
    '''Represents a view for list of "OrderItem" objects.
    '''
    queryset = OrderItem.objects.all().order_by('pk')
    serializer_class = OrderItemSerializer
