import os.path
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django_apscheduler import util
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from django.conf import settings
from django.core.management.base import BaseCommand

from mainapp.models import OrderItem

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SPREADSHEET_ID = '1I8CvbwvJpcTeibzXnj9RS9MxQqy2clLTooE46E2rmbY'
SHEET_NAME = 'Data'
PROCESS_ROW_COUNT = 500
FIRST_DATA_ROW = 2

def update_db():
    '''Updates database records based on Google Sheets file.
    '''
    # Checking credentials
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    else:
        return
    # Updating data in database
    try:
        # Getting the Google Sheets API service
        service = build('sheets', 'v4', credentials=creds)
        # Calling the Google Sheets API
        sheet = service.spreadsheets()
        # Getting data from the sheet and updating database
        next_row = FIRST_DATA_ROW
        seen_ids = set()
        while True:
            # Getting data
            data_range_name = f'{SHEET_NAME}!A{next_row}:D{next_row + PROCESS_ROW_COUNT}'
            result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                        range=data_range_name).execute()
            rows = result.get('values', [])
            # Exiting loop if no more data
            if not rows:
                break
            # Processing every row of the data
            for row in rows:
                try:
                    # Reading cells
                    id = int(row[0])
                    seen_ids.add(id)
                    order_number = int(row[1])
                    cost_usd = float(row[2])
                    cost_rub = cost_usd * 80
                    delivery_date = datetime.strptime(row[3], '%d.%m.%Y')
                    # Updating database
                    OrderItem.objects.update_or_create(pk=id, defaults={
                        'order_number': order_number,
                        'cost_usd': cost_usd,
                        'cost_rub': cost_rub,
                        'delivery_date': delivery_date
                    })
                except Exception as error:
                    print(error)
                    continue
            # Going to the next portion of data
            next_row += PROCESS_ROW_COUNT
        # Deleting records that are not in the Google Sheets document
        OrderItem.objects.exclude(pk__in=seen_ids).delete()
    except HttpError as error:
        print(error)

@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
    '''Deletes APScheduler job execution entries older than 'max_age' from the database.
    '''
    DjangoJobExecution.objects.delete_old_job_executions(max_age)

class Command(BaseCommand):
    '''Represents a handler of "runscheduler" command.
    '''
    help = 'Runs scheduler.'

    def handle(self, *args, **options):
        # Creating scheduler
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), 'default')
        # Adding jobs
        scheduler.add_job(
            update_db,
            trigger=CronTrigger(minute='*/1'),
            id='update_db',
            max_instances=1,
            replace_existing=True
        )
        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week='mon', hour='00', minute='00'
            ),
            id='delete_old_job_executions',
            max_instances=1,
            replace_existing=True
        )
        # Starting scheduler
        try:
            scheduler.start()
        except KeyboardInterrupt:
            scheduler.shutdown()
