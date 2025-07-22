from django.urls import path
from mailer.apps import MailerConfig
from .views import HomeTemplateView, MailingListView, MailingDetailView, MailingCreateView, MailingUpdateView, \
    MailingDeleteView, MessageListView, MessageDetailView, MessageCreateView, MessageUpdateView, MessageDeleteView, \
    RecipientListView, RecipientDetailView, RecipientCreateView, RecipientUpdateView, RecipientDeleteView, \
    MailingStatsView, MailingDetailStatsView, mailing_complete_view, mailing_launch_view, mailing_run_view, \
    MailingDisableView

app_name = MailerConfig.name

urlpatterns = [
    path('', HomeTemplateView.as_view(), name='home'),
    path("mailing_list/", MailingListView.as_view(), name="mailing_list"),
    path("mailing/<int:pk>/", MailingDetailView.as_view(), name="mailing_detail"),
    path("mailing_create/", MailingCreateView.as_view(), name="mailing_create"),
    path("mailing/<int:pk>/update/", MailingUpdateView.as_view(), name="mailing_update"),
    path("mailing/<int:pk>/disable_switch/", MailingDisableView.as_view(), name="mailing_disable_switch"),
    path("mailing/<int:pk>/delete/", MailingDeleteView.as_view(), name="mailing_delete"),
    path("mailing/<int:pk>/run_mailing/", mailing_run_view, name="mailing_run"),
    path("mailing/<int:pk>/launch/", mailing_launch_view, name="mailing_launch"),
    path("mailing/<int:pk>/complete/", mailing_complete_view, name="mailing_complete"),
    path("message_list/", MessageListView.as_view(), name="message_list"),
    path("message/<int:pk>/", MessageDetailView.as_view(), name="message_detail"),
    path("message_create/", MessageCreateView.as_view(), name="message_create"),
    path("message/<int:pk>/update/", MessageUpdateView.as_view(), name="message_update"),
    path("message/<int:pk>/delete/", MessageDeleteView.as_view(), name="message_delete"),
    path("recipient_list/", RecipientListView.as_view(), name="recipient_list"),
    path("recipient/<int:pk>/", RecipientDetailView.as_view(), name="recipient_detail"),
    path("recipient_create/", RecipientCreateView.as_view(), name="recipient_create"),
    path("recipient/<int:pk>/update/", RecipientUpdateView.as_view(), name="recipient_update"),
    path("recipient/<int:pk>/delete/", RecipientDeleteView.as_view(), name="recipient_delete"),
    path("mailing_detail_stats/<int:pk>/", MailingDetailStatsView.as_view(), name="mailing_stats_detail"),
    path("stats/", MailingStatsView.as_view(), name="mailing_stats"),
    path('mailing_complete_func/<int:pk>/', mailing_complete_view, name='mailing_complete_func'),
    #    path('run_mailing/<int:id>/', execute_service_function, name='run_mailing'),
]
