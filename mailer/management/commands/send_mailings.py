from django.core.management.base import BaseCommand

from mailer.models import Mailing
from mailer.services import send_mailing


class Command(BaseCommand):
    help = "Отправка рассылок"

    def handle(self, *args, **options):
        mailings = Mailing.objects.filter(status="Launched")
        for mailing in mailings:
            try:
                send_mailing(mailing.id)
            except Exception as e:
                print(f"Ошибка рассылки ID: {mailing.id} {mailing.message.title}: {e} - Пропущена")
