from django import forms
from django.utils import timezone
from django.core.exceptions import ValidationError
from .models import Mailing, Recipient, Message


class RecipientForm(forms.ModelForm):
    """Форма для получателя: email, ФИО, комментарий"""
    class Meta:
        model = Recipient
        fields = ['email', 'full_name', 'comment']


class MessageForm(forms.ModelForm):
    """Форма для сообщения: тема и текст письма"""
    class Meta:
        model = Message
        fields = ['subject_letter', 'body_letter']


class MailingForm(forms.ModelForm):
    """Форма для рассылки с валидацией дат"""
    class Meta:
        model = Mailing
        fields = ['start_time', 'end_time', 'message', 'recipients']

    def clean(self):
        """Валидация: start_time не в прошлом и раньше end_time"""
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if start_time and end_time:
            if start_time >= end_time:
                raise ValidationError({
                    'end_time': 'Дата окончания должна быть позже даты начала'
                })

        if start_time and start_time < timezone.now():
            raise ValidationError({
                'start_time': 'Дата начала не может быть в прошлом'
            })

        return cleaned_data
