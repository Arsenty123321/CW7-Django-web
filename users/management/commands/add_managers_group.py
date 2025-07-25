from django.core.management import BaseCommand
from django.contrib.auth.models import Group, Permission

from dotenv import load_dotenv

load_dotenv(override=True)


class Command(BaseCommand):
    def handle(self, *args, **kwargs):

        group_name = 'mailing_manager'

        # Создаем группу
        managers_group, created = Group.objects.get_or_create(name=group_name)

        # Получаем нужные разрешения
        can_view_recipient_permission = Permission.objects.get(codename='can_view_recipient')
        can_view_message_permission = Permission.objects.get(codename='can_view_message')
        can_view_mailing_permission = Permission.objects.get(codename='can_view_mailing')
        can_disable_mailing_permission = Permission.objects.get(codename='can_disable_mailing')
        can_block_user_permission = Permission.objects.get(codename='can_block_user')

        # Добавляем разрешения в группу
        managers_group.permissions.add(can_view_recipient_permission, can_view_message_permission,
                                       can_view_mailing_permission, can_block_user_permission,
                                       can_disable_mailing_permission)

        if created:
            self.stdout.write(self.style.SUCCESS(f'Группа "{group_name}" была успешно создана.'))
        else:
            self.stdout.write(self.style.WARNING(f'Группа "{group_name}" уже существует.'))
