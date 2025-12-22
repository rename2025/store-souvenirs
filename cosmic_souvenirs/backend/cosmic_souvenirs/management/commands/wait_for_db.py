import time
from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError


class Command(BaseCommand):
    """Django command to wait for database to be available"""

    def handle(self, *args, **options):
        self.stdout.write('Waiting for database...')
        db_conn = None
        max_retries = 30
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                db_conn = connections['default']
                db_conn.cursor()
                self.stdout.write(self.style.SUCCESS('Database available!'))
                return
            except OperationalError:
                retry_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Database unavailable, '
                                      f'waiting 1 second... ({retry_count}/{max_retries})')
                )
                time.sleep(1)
        
        self.stdout.write(
            self.style.ERROR('Database not available after maximum retries!')
        )
