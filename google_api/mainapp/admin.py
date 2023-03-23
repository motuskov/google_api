from django.contrib import admin

from .models import (
    OrderItem,
    UpdateExecution,
    UpdateExecutionError,
)

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

class UpdateExecutionErrorInLine(admin.TabularInline):
    '''Represents an error occurred during a process of updating OrderItem table in the 
    administration interface.
    '''
    model = UpdateExecutionError
    fields = [
        'short_description',
    ]

@admin.register(UpdateExecution)
class UpdateExecutionAdmin(admin.ModelAdmin):
    '''Represents a process of updating OrderItem table in the administration interface.
    '''
    list_display = [
        'created',
        'status',
        'document_timestamp',
        'usd_exchange_rate',
    ]
    inlines = [
        UpdateExecutionErrorInLine
    ]

@admin.register(UpdateExecutionError)
class UpdateExecutionErrorAdmin(admin.ModelAdmin):
    '''Represents an error occurred during a process of updating OrderItem table in the 
    administration interface.
    '''
    list_display = [
        'update_execution',
        'short_description',
    ]
