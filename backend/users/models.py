from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.crypto import get_random_string

class User(AbstractUser):
    email = models.EmailField(
        'email address',
        max_length=254,
        unique=True,
    )
    username = models.CharField(
        'username',
        max_length=150,
        unique=True,
    )
    first_name = models.CharField(
        'first name',
        max_length=150,
    )
    last_name = models.CharField(
        'last name',
        max_length=150,
    )
    is_subscribed = models.BooleanField(
        'subscribed',
        default=False,
    )
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_users',  # Уникальное имя для groups
        blank=True,
        verbose_name='groups',
        help_text='The groups this user belongs to.',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_users',  # Уникальное имя для permissions
        blank=True,
        verbose_name='user permissions',
        help_text='Specific permissions for this user.',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        ordering = ['id']
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def __str__(self):
        return self.username


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='follower'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='author'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_subscription'
            )
        ]
        verbose_name = 'subscription'
        verbose_name_plural = 'subscriptions'

    def __str__(self):
        return f'{self.user} follows {self.author}'