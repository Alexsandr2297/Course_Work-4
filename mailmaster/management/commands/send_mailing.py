from django.core.management.base import BaseCommand
from mailmaster.models import Mailing


class Command(BaseCommand):
    help = 'Запуск рассылки'

    def add_arguments(self, parser):
        parser.add_argument('mailing_id', type=int)

    def handle(self, *args, **options):
        mailing = Mailing.objects.get(id=options['mailing_id'])
        result = mailing.send_mailing()
        self.stdout.write(result)