from django.core.management import BaseCommand
from users.models import User
import os
from dotenv import load_dotenv

load_dotenv(override=True)

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        user = User.objects.create(email=os.getenv('SUPER_USER_LOGIN_NAME'))
        user.set_password(os.getenv('SUPER_USER_PASSWORD'))
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save()
