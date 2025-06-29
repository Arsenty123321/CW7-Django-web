from django.urls import path
from mailer.apps import MailerConfig
from .views import HomeTemplateView, MailingListView, MailingDetailView, MailingCreateView, MailingUpdateView, \
    MailingDeleteView

app_name = MailerConfig.name

urlpatterns = [
    path('', HomeTemplateView.as_view(), name='home'),
    path("mailing_list/", MailingListView.as_view(), name="mailing_list"),
    path("mailing/<int:pk>/", MailingDetailView.as_view(), name="mailing_detail"),
    path("create/", MailingCreateView.as_view(), name="mailing_create"),
    path("mailing/<int:pk>/update/", MailingUpdateView.as_view(), name="mailing_update"),
    path("mailing/<int:pk>/delete/", MailingDeleteView.as_view(), name="mailing_delete"),
]
