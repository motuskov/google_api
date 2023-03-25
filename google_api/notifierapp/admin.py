from django.contrib import admin

from .models import Subscription

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    '''Represents user's subscription in administration interface.
    '''
    list_display = (
        'chat_id',
    )
    search_fields = (
        'chat_id',
    )
