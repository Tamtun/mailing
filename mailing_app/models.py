from django.db import models
from django.conf import settings

class Client(models.Model):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    comment = models.TextField(blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='clients',
        verbose_name='Владелец'
    )

    def __str__(self):
        return f"{self.full_name} <{self.email}>"

    class Meta:
        permissions = [
            ('can_manage_clients', 'Может управлять клиентами'),
        ]

class Message(models.Model):
    subject = models.CharField(max_length=255)
    body = models.TextField()
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='Владелец'
    )

    def __str__(self):
        return self.subject

    class Meta:
        permissions = [
            ('can_manage_messages', 'Может управлять сообщениями'),
        ]

class Mailing(models.Model):
    STATUS_CHOICES = [
        ('Создана', 'Создана'),
        ('Запущена', 'Запущена'),
        ('Завершена', 'Завершена'),
    ]
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Создана')
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    clients = models.ManyToManyField(Client)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Рассылка: {self.message.subject} ({self.status})"

    class Meta:
        permissions = [
            ('can_manage_mailings', 'Может управлять рассылками'),
        ]

class Attempt(models.Model):
    STATUS_CHOICES = [
        ('Успешно', 'Успешно'),
        ('Не успешно', 'Не успешно'),
    ]

    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    server_response = models.TextField()

    def __str__(self):
        return f"{self.mailing} — {self.status} @ {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
