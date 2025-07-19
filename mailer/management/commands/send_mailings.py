from django.core.management.base import BaseCommand

from mailer.models import Mailing
from mailer.services import send_mailing


class Command(BaseCommand):
    help = "Отправка рассылок"

    def add_arguments(self, parser):
        parser.add_argument(
            '--id',
            type=int,
            help='Запуск рассылки по конкретному ID'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Запуск всех рассылок независимо от статуса'
        )

    def handle(self, *args, **options):
        mailing_id = options.get('id')
        all_mailings = options.get('all')

        if mailing_id:
            print(f"Запуск рассылки с ID: {mailing_id}")
            mailings = Mailing.objects.filter(id=mailing_id)
        elif all_mailings:
            print("Запуск всех рассылок (независимо от статуса)")
            mailings = Mailing.objects.all()
        else:
            print("Запуск всех рассылок со статусом 'Launched' (Запущена)")
            mailings = Mailing.objects.filter(status="Launched")

        for mailing in mailings:
            try:
                send_mailing(mailing.id)
            except Exception as e:
                print(f"Ошибка рассылки ID: {mailing.id} {mailing.message.title}: {e} - Пропущена")
