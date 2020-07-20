
from time import sleep
from django.db import connections
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    """custome command to make the app wait for database to be ready

    Args:
        BaseCommand (MODULE): a django built-in module to create custome commands
    """    
    def handle(self, *args, **options):
        """waits 5 seconds and if the data base was ready it will pass
        """        
        self.stdout.write("Waiting for database to ready ...")
        db_con = None
        while not db_con:
            try:
                db_con = connections['default']
            except OperationalError:
                self.stdout.wirte("Database unavailable waiting ...")
                sleep(5)
        self.stdout.write(self.style.SUCCESS("Database is now available!"))