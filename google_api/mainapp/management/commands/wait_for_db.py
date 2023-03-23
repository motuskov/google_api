import time

from django.db import connections
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    '''Represents a handler of "wait_for_db" command.
    '''
    help = 'Waits for DB connection appearing.'

    def handle(self, *args, **options):
        db_conn = None
        while not db_conn:
            try:
                db_conn = connections['default']
            except OperationalError:
                time.sleep(1)
