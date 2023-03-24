from django.db import models

class Subscription(models.Model):
    '''Represents user's subscription.
    '''
    chat_id = models.IntegerField(
        unique=True,
        help_text='Chat ID of the subscribed user.'
    )
