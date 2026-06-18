"""Модели сервиса рассылок."""

from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.conf import settings


class Recipient(models.Model):
    """Получатель: email, ФИО, комментарий. Привязан к владельцу."""

    email = models.CharField(unique=True, max_length=100, verbose_name="Email", help_text="Введите email")
    full_name = models.CharField(max_length=255, verbose_name="Ф.И.О", help_text="Полное имя получателя")
    comment = models.TextField(verbose_name="Коментарий", blank=True, null=True,
                               help_text="Дополнительная информация о получателе")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Владелец")

    class Meta:
        verbose_name = "Получатель"
        verbose_name_plural = "Получатели"
        permissions = [
            ("can_view_all", "Может просматривать всех получателей"),
        ]

    def __str__(self):
        return self.email


class Message(models.Model):
    """Сообщение: тема и тело письма."""
    subject_letter = models.CharField(max_length=100, verbose_name="Тема письма",
                                      help_text="Введите тему письма")
    body_letter = models.TextField(verbose_name="Тело письма", blank=True, null=True, help_text="Введите тело письма")

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"

    def __str__(self):
        return self.subject_letter


class Mailing(models.Model):
    """Рассылка: период, статус, сообщение, получатели, владелец."""
    STATUS_CHOICES = [
        ('Создана', 'Создана'),
        ('Запущена', 'Запущена'),
        ('Завершена', 'Завершена'),
    ]

    start_time = models.DateTimeField(verbose_name="Дата и время начала отправки")
    end_time = models.DateTimeField(verbose_name="Дата и время окончания отправки")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Создана', verbose_name="Статус")
    message = models.ForeignKey(Message, on_delete=models.CASCADE, verbose_name="Сообщение")
    recipients = models.ManyToManyField(Recipient, verbose_name="Получатели")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Владелец")
    is_active = models.BooleanField(default=True, verbose_name="Активна")

    def can_send(self):
        """Проверка, можно ли отправлять рассылку в данный момент"""
        now = timezone.now()
        return self.start_time <= now <= self.end_time

    def update_status(self):
        """Динамическое обновление статуса рассылки"""
        now = timezone.now()

        if now < self.start_time:
            new_status = 'Создана'
        elif self.start_time <= now <= self.end_time:
            new_status = 'Запущена'
        else:
            new_status = 'Завершена'

        if self.status != new_status:
            self.status = new_status
            self.save(update_fields=['status'])

    def send_mailing(self):
        """Запуск рассылки с проверкой времени и batch-логированием"""
        # Обновляем статус
        self.update_status()

        # Проверка времени
        now = timezone.now()
        if not (self.start_time <= now <= self.end_time):
            raise ValidationError('Время для отправки не подходит')

        # Batch создание записей
        attempts = []

        for recipient in self.recipients.all():
            try:
                send_mail(
                    self.message.subject_letter,
                    self.message.body_letter,
                    settings.DEFAULT_FROM_EMAIL,
                    [recipient.email],
                )
                attempts.append(MailingAttempt(
                    mailing=self,
                    recipient=recipient,
                    status='Успешно',
                    server_response="Письмо отправлено"
                ))
            except Exception as e:
                attempts.append(MailingAttempt(
                    mailing=self,
                    recipient=recipient,
                    status='Не успешно',
                    error_message=str(e),
                    server_response=f"Ошибка: {str(e)}"
                ))

        # Одна операция в БД вместо многих
        MailingAttempt.objects.bulk_create(attempts)

        return "Рассылка выполнена"

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"
        permissions = [
            ("can_view_all", "Может просматривать все рассылки"),
            ("can_disable_mailing", "Может отключать рассылки"),
        ]

    def __str__(self):
        return f"Рассылка {self.id} - {self.status}"


class MailingAttempt(models.Model):
    """Логирование попыток отправки"""

    STATUS_CHOICES = [
        ('Успешно', 'Успешно'),
        ('Не успешно', 'Не успешно'),
    ]

    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE, related_name='attempts')
    recipient = models.ForeignKey(Recipient, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    server_response = models.TextField(blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    attempt_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Попытка рассылки"
        verbose_name_plural = "Попытки рассылок"
        ordering = ['-attempt_time']

    def __str__(self):
        return f"{self.recipient.email} - {self.status} ({self.attempt_time})"
