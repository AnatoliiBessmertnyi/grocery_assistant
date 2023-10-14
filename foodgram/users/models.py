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


class Subscription(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='subscription'
    )
    subscriber = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Подписчик',
        related_name='subscriber'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'subscriber'], name='unique_subscriptions'
            )
        ]

    def __str__(self):
        return f'{self.subscriber.username} подписан на {self.author.username}'
