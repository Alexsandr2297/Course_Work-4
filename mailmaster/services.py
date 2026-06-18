from .models import Mailing, MailingAttempt
from django.core.cache import cache

"""Сервис для работы с рассылками и кешированием"""

def get_mailing_stats(mailing):
    """Статистика одной рассылки: всего, успешно, не успешно."""
    attempts = mailing.attempts.all()
    return {
        'total': attempts.count(),
        'success': attempts.filter(status='Успешно').count(),
        'failed': attempts.filter(status='Не успешно').count(),
    }


def get_global_stats():
    """Глобальная статистика по всем рассылкам"""
    return {
        'total_mailings': Mailing.objects.count(),
        'total_attempts': MailingAttempt.objects.count(),
        'success_attempts': MailingAttempt.objects.filter(status='Успешно').count(),
        'failed_attempts': MailingAttempt.objects.filter(status='Не успешно').count(),
    }


class MailingService:
    """Сервис с кешированием списков рассылок"""

    @staticmethod
    def get_all_mailings():
        """Все рассылки с кешем на 15 минут."""
        cache_key = 'mailings_all'
        mailings = cache.get(cache_key)
        if not mailings:
            mailings = Mailing.objects.all()
            cache.set(cache_key, mailings, 60 * 15)
        return mailings

    @staticmethod
    def get_user_mailings(user_id):
        """Рассылки пользователя с кешем на 15 минут."""
        cache_key = f'mailings_user_{user_id}'
        mailings = cache.get(cache_key)
        if not mailings:
            mailings = Mailing.objects.filter(owner_id=user_id)
            cache.set(cache_key, mailings, 60 * 15)
        return mailings