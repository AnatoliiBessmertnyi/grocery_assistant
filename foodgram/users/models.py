from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

username_validator = RegexValidator(
    regex=r'^[\w.@+-]+$',
    message=(
        'Имя пользователя должно состоять из буквенно-цифровых символов, '
        'а также знаков ".", "@", "+", "-" и не содержать других символов.'
    ),
)


class CustomUser(AbstractUser):
    """Пользовательская модель пользователя с уникальным идентификатором
    через email."""
    username = models.CharField(
        unique=True,
        max_length=settings.MAX_LENGHT,
        validators=[username_validator],
        verbose_name='Имя пользователя',
    )
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

    @property
    def is_admin(self):
        return self.is_superuser

    def __str__(self):
        return self.email
