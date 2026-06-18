from django.core.management.base import BaseCommand
from users.models import User
from django.contrib.auth.models import Permission


class Command(BaseCommand):
    help = 'Назначает права менеджера пользователю'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str)

    def handle(self, *args, **options):
        user = User.objects.get(email=options['email'])
        user.is_staff = True

        # Права для рассылок
        mailing_perms = Permission.objects.filter(content_type__app_label='mailmaster')
        user.user_permissions.add(*mailing_perms)

        # Права для пользователей
        user_perms = Permission.objects.filter(content_type__app_label='users')
        user.user_permissions.add(*user_perms)

        user.save()
        self.stdout.write(self.style.SUCCESS(f'Менеджер: {user.email}'))