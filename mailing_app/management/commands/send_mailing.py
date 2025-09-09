from django.core.management.base import BaseCommand, CommandError
from mailing_app.models import Mailing, Attempt
from django.core.mail import send_mail

class Command(BaseCommand):
    help = 'Отправляет рассылку по указанному ID'

    def add_arguments(self, parser):
        parser.add_argument('mailing_id', type=int)

    def handle(self, *args, **options):
        mailing_id = options['mailing_id']
        try:
            mailing = Mailing.objects.get(pk=mailing_id)
        except Mailing.DoesNotExist:
            raise CommandError(f'Рассылка с ID {mailing_id} не найдена.')

        self.stdout.write(f'Отправка рассылки #{mailing_id}...')

        for client in mailing.clients.all():
            try:
                send_mail(
                    subject=mailing.message.subject,
                    message=mailing.message.body,
                    from_email='noreply@example.com',
                    recipient_list=[client.email],
                    fail_silently=False,
                )
                Attempt.objects.create(
                    mailing=mailing,
                    status='Успешно',
                    server_response='Письмо отправлено успешно'
                )
                self.stdout.write(f'✅ {client.email} — отправлено')
            except Exception as e:
                Attempt.objects.create(
                    mailing=mailing,
                    status='Не успешно',
                    server_response=str(e)
                )
                self.stdout.write(f'❌ {client.email} — ошибка: {e}')

        mailing.status = 'Запущена'
        mailing.save()
        self.stdout.write(self.style.SUCCESS('Рассылка завершена'))
