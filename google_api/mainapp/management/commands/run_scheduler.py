import asyncio
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django_apscheduler import util
from googleapiclient.errors import HttpError

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.cache import cache

from mainapp.models import (
    OrderItem,
    UpdateExecution,
)
from mainapp.utils import (
    get_exchange_rate,
    get_google_credentials,
    get_google_document_modified_time,
    read_google_spreadsheet_data,
)
from notifierapp.utils import send_expire_notification
from notifierapp.models import Subscription

def update_db():
    '''Updates database records based on Google Sheets file.
    '''
    # Creating the update process record
    update_execution = UpdateExecution.objects.create()

    # Getting USD exchange rate
    usd_exchange_rate = cache.get('usd_exchange_rate')
    if not usd_exchange_rate:
        try:
            usd_exchange_rate = get_exchange_rate(settings.EXCHANGE_RATE_URL, 'USD')
            if not usd_exchange_rate:
                update_execution.add_error('USD exchange rate cannot be retrieved')
                return
            cache.set(
                'usd_exchange_rate',
                usd_exchange_rate,
                settings.EXCHANGE_RATE_EXPIRATION_TIME
            )
        except Exception as error:
            update_execution.add_error(
                'An error occurred during retrieving USD exchange rate',
                error_details=error
            )
            return
    update_execution.usd_exchange_rate = usd_exchange_rate
    update_execution.save()

    # Checking credentials
    creds = get_google_credentials(settings.GOOGLE_API_TOKEN_FILENAME, settings.GOOGLE_API_SCOPES)
    if not creds:
        update_execution.add_error(
            'Credentials file "token.json" was not found in the project directory or it is not '
            'valid.'
        )
        return

    # Getting the previous document timestamp and the previous usd exchange rate
    try:
        last_successful_update_execution = UpdateExecution.objects.filter(
            status='success').exclude(pk=update_execution.pk).latest('created')
        previous_document_timestamp = last_successful_update_execution.document_timestamp
        previous_usd_exchange_rate = last_successful_update_execution.usd_exchange_rate
    except UpdateExecution.DoesNotExist:
        previous_document_timestamp = None
        previous_usd_exchange_rate = None

    # Checking if full update is needed
    if settings.GOOGLE_API_CHECK_DOCUMENT_MODIFIED_TIME:
        try:

            # Getting and saving the document timestamp
            document_timestamp = get_google_document_modified_time(creds, settings.SPREADSHEET_ID)
            update_execution.document_timestamp = document_timestamp
            update_execution.save()

            # Updating only USD cost if the document has not been changed and USD exchange rate has
            # changed
            if document_timestamp == previous_document_timestamp:
                if usd_exchange_rate != previous_usd_exchange_rate:
                    OrderItem.refresh_cost_rub(usd_exchange_rate)
                return

        except HttpError as error:
            update_execution.add_error(
                'A critical error occurred during retrieving the document modification time',
                error_details=error
            )

    # Updating data in database
    try:

        # Getting data from the Google Sheets document
        document_data, document_errors = read_google_spreadsheet_data(
            creds,
            settings.SPREADSHEET_ID,
            settings.SHEET_NAME,
            settings.FIRST_DATA_ROW,
            settings.GOOGLE_API_PROCESS_ROW_COUNT
        )

        # Deleting database records that do not exist in the document
        OrderItem.objects.exclude(pk__in=document_data).delete()

        # Updating existing records
        existing_order_items = OrderItem.objects.all()
        order_items_to_update = []
        for order_item in existing_order_items:
            document_order_item = document_data[order_item.pk]
            if ((order_item.order_number,
                 order_item.cost_usd,
                 order_item.delivery_date) != document_order_item or
                usd_exchange_rate != previous_usd_exchange_rate):
                (order_item.order_number,
                 order_item.cost_usd,
                 order_item.delivery_date) = document_order_item
                order_item.cost_rub = order_item.cost_usd * usd_exchange_rate
                order_items_to_update.append(order_item)
            del document_data[order_item.pk]
        OrderItem.objects.bulk_update(
            order_items_to_update,
            ['order_number', 'cost_usd', 'cost_rub', 'delivery_date']
        )

        # Creating new records
        order_items_to_create = []
        for id, fields in document_data.items():
            order_items_to_create.append(OrderItem(
                pk=id,
                order_number=fields[0],
                cost_usd=fields[1],
                cost_rub=fields[1] * usd_exchange_rate,
                delivery_date=fields[2]
            ))
        OrderItem.objects.bulk_create(order_items_to_create)

        # Saving errors to database
        for error in document_errors:
            update_execution.add_error(error['description'], error['details'])

    except HttpError as error:
        update_execution.add_error(
            'A critical error occurred during the processing of the document',
            error_details=error
        )

def check_expiration():
    '''Checks expiration status and sends notifications.
    '''
    # Getting new expired items
    new_expired_order_items = OrderItem.update_expiration()

    # Sending notifications
    if new_expired_order_items:
        new_expired_order_items_str = [
            str(new_expired_order_item) for new_expired_order_item in new_expired_order_items
        ]
        subscriptions = Subscription.objects.all()
        for subscription in subscriptions:
            asyncio.run(send_expire_notification(
                settings.TELEGRAM_BOT_TOKEN,
                subscription.chat_id,
                new_expired_order_items_str
            ))

@util.close_old_connections
def delete_old_executions(max_age=604_800):
    '''Deletes execution entries older than 'max_age' from the database.
    '''
    DjangoJobExecution.objects.delete_old_job_executions(max_age)
    UpdateExecution.delete_old_executions(max_age)

class Command(BaseCommand):
    '''Represents a handler of "run_scheduler" command.
    '''
    help = 'Runs scheduler.'

    def handle(self, *args, **options):
        # Creating scheduler
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), 'default')
        # Adding jobs
        scheduler.add_job(
            update_db,
            trigger=CronTrigger(second='*/20'),
            id='update_db',
            max_instances=1,
            replace_existing=True
        )
        scheduler.add_job(
            delete_old_executions,
            trigger=CronTrigger(
                day_of_week='mon', hour='00', minute='00'
            ),
            id='delete_old_executions',
            max_instances=1,
            replace_existing=True
        )
        scheduler.add_job(
            check_expiration,
            trigger=CronTrigger(second='*/25'),
            id='check_expiration',
            max_instances=1,
            replace_existing=True
        )
        # Starting scheduler
        try:
            scheduler.start()
        except KeyboardInterrupt:
            scheduler.shutdown()
