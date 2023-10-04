from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Пользовательская модель пользователя."""
    email = models.EmailField(
        unique=True,
        max_length=settings.MAX_LENGHT,
        verbose_name='Электронная почта',
    )
    first_name = models.CharField(
        max_length=settings.MAX_LENGHT,
        blank=True,
        verbose_name='Имя',
    )
    last_name = models.CharField(
        max_length=settings.MAX_LENGHT,
        blank=True,
        verbose_name='Фамилия',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        ordering = ['id']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email
