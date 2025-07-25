from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm

from mailer.forms import StyleFormMixin
from .models import User


class UserRegisterForm(StyleFormMixin, UserCreationForm):
    class Meta:
        model = User
        fields = ("email", "password1", "password2")


class UserProfileForm(ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "avatar", "phone", "country"]


class UserDisableForm(ModelForm):
    class Meta:
        model = User
        fields = ("id", "is_active")
