import datetime

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django_apscheduler import util

from django.conf import settings
from django.core.management.base import BaseCommand

from mainapp.models import OrderItem


def test_job():
    OrderItem.objects.create(
        order_number=123456,
        cost_usd=10.00,
        cost_rub=20.00,
        delivery_date=datetime.date(2023, 2, 5)
    )

@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
    '''
    Deletes APScheduler job execution entries older than 'max_age'
    from the database.
    '''
    DjangoJobExecution.objects.delete_old_job_executions(max_age)

class Command(BaseCommand):
    help = 'Runs scheduler.'

    def handle(self, *args, **options):
        # Creating scheduler
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), 'default')
        # Adding jobs
        scheduler.add_job(
            test_job,
            trigger=CronTrigger(minute='*/1'),
            id='test_job',
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
