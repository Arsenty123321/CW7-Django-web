from django.urls import path
from mailer.apps import MailerConfig
from .views import HomeTemplateView

app_name = MailerConfig.name

urlpatterns = [
    path('', HomeTemplateView.as_view(), name='home'),
]
