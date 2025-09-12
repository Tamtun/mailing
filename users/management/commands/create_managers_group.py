from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from users.models import CustomUser

class Command(BaseCommand):
    help = 'Создаёт группу "Менеджеры" и добавляет пользователей с ролью manager'

    def handle(self, *args, **kwargs):
        group_name = 'Менеджеры'
        group, created = Group.objects.get_or_create(name=group_name)

        if created:
            self.stdout.write(self.style.SUCCESS(f'Группа "{group_name}" создана.'))
        else:
            self.stdout.write(f'Группа "{group_name}" уже существует.')

        managers = CustomUser.objects.filter(role='manager')
        for user in managers:
            user.groups.add(group)
            self.stdout.write(f'Пользователь {user.email} добавлен в группу.')

        self.stdout.write(self.style.SUCCESS('Готово.'))
