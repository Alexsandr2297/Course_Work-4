from django.contrib.auth.forms import UserCreationForm
from django import forms
from users.models import User

"""Формы для приложения пользователей"""

class FormStylingMixin:
    """Миксин для стилизации полей формы."""
    placeholders = {
        'email': 'example@mail.ru',
        'phone_number': '79001234567',
        'country': 'Россия',
        'password1': 'Введите пароль',
        'password2': 'Повторите пароль',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control'
            })
            if name in self.placeholders:
                field.widget.attrs['placeholder'] = self.placeholders[name]


class UserRegisterForm(FormStylingMixin, UserCreationForm):
    """Форма регистрации пользователя."""
    class Meta:
        model = User
        fields = ("email", "phone_number", "country", "password1", "password2")

    def clean_phone_number(self):
        """Валидация телефона: только цифры."""
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number and not phone_number.isdigit():
            raise forms.ValidationError('Номер телефона должен содержать только цифры.')
        return phone_number
