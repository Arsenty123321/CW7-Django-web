from django.contrib.auth.forms import UserCreationForm
from mailer.forms import StyleFormMixin
from .models import User


class UserRegisterForm(StyleFormMixin, UserCreationForm):
    class Meta:
        model = User
        fields = ("email", "password1", "password2")
