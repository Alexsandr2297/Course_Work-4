from django.contrib.auth.models import AbstractUser
from django.db import models

"""Модель пользователя с аутентификацией по email."""

class User(AbstractUser):
    """    Кастомная модель пользователя. Вход осуществляется по email, поле username отсутствует."""
    username = None
    email = models.EmailField(unique=True, verbose_name="Email")

    phone_number = models.CharField(max_length=15, blank=True, null=True, help_text="Введите номер телефона")
    avatar = models.ImageField(upload_to='avatars/', verbose_name="Аватар", blank=True, null=True, help_text="Загрузите аватар")
    country = models.CharField(max_length=30, blank=True, null=True, help_text="Введите страну")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []


    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        permissions = [
            ("can_view_users", "Может просматривать список пользователей"),
            ("can_block_user", "Может блокировать пользователей"),
        ]

    def __str__(self):
        return self.email
