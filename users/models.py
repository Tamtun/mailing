from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('user', 'Пользователь'),
        ('manager', 'Менеджер'),
    )

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    is_blocked = models.BooleanField(default=False)

    email = models.EmailField(unique=True, verbose_name='Email')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='Аватар')
    phone_number = models.CharField(max_length=20, blank=True, verbose_name='Телефон')
    country = models.CharField(max_length=100, blank=True, verbose_name='Страна')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"
