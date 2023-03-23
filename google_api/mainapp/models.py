from django.db import models
from django.utils import timezone

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
    delivery_date = models.DateField(
        help_text='The date by which the item must be delivered.'
    )

    @classmethod
    def refresh_cost_rub(cls, usd_exchange_rate):
        '''Refreshes the cost in USD for all database records.

        Parameters:
            usd_exchange_rate (float): New value of USD exchange rate
        '''
        order_items = cls.objects.all()
        for order_item in order_items:
            order_item.cost_rub = float(order_item.cost_usd) * usd_exchange_rate
        cls.objects.bulk_update(order_items, ['cost_rub'])

class UpdateExecution(models.Model):
    '''Represents a process of updating OrderItem table.
    '''
    STATUSES = (
        ('success', 'Executed successfully'),
        ('fail', 'A critical error occurred'),
        ('partly_fail', 'There are some errors'),
    )
    created = models.DateTimeField(
        auto_now_add=True,
        help_text='Date and time of the updating process.'
    )
    status = models.CharField(
        max_length=11,
        choices=STATUSES,
        default='success',
        help_text='Status of process execution.'
    )
    document_timestamp = models.CharField(
        max_length=30,
        blank=True,
        help_text='The information about date and time of document changing.'
    )
    usd_exchange_rate = models.FloatField(
        null=True,
        blank=True,
        help_text='USD exchange rate used to calculate cost in USD.'
    )

    def add_error(self, error_short_description, fatal=True, error_details=''):
        '''Adds the error.

        Parameters:
            fatal (bool): True if the error is fatal for current process
            error_short_description (str): Short description of the error
            error_details (str): Detaild description of the error
        '''
        # Changing status of the update process record
        if fatal and self.status != 'fail':
            self.status = 'fail'
        elif not fatal and self.status == 'success':
            self.status = 'part_fail'
        self.save()
        # Adding the error
        self.errors.create(
            short_description=error_short_description,
            details=error_details
        )

    @classmethod
    def delete_old_executions(cls, max_age):
        '''Deletes all UpdateExecutions older than 'max_age' seconds.

        Parameters:
            max_age (int): Number of seconds to indicate old records
        '''
        current_time = timezone.now()
        oldest_valid_time = current_time - timezone.timedelta(seconds=max_age)
        cls.objects.filter(created__lt=oldest_valid_time).delete()

class UpdateExecutionError(models.Model):
    '''Represents an error occurred during a process of updating OrderItem table.
    '''
    update_execution = models.ForeignKey(
        UpdateExecution,
        on_delete=models.CASCADE,
        related_name='errors',
        help_text='The update execution process during execution of which the error occurred.'
    )
    short_description = models.CharField(
        max_length=100,
        help_text='Short description of the error.'
    )
    details = models.TextField(
        blank=True,
        help_text='Detailed information about the error.'
    )
