from django.contrib import admin
from mailer.models import MailingRecipient, MailMessage, Mailing, MailingAttempt


@admin.register(MailingRecipient)
class MailingRecipientAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "full_name", "owner")
    list_filter = ("id",)
    search_fields = ("email", "owner",)


@admin.register(MailMessage)
class MailMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "owner")
    search_fields = ("title", "owner",)


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ("id", "message", "owner", "status")
    search_fields = ("owner",)


@admin.register(MailingAttempt)
class MailingAttemptAdmin(admin.ModelAdmin):
    list_display = ("id", "attempt_send_data", "attempt_status", "mailing")
    search_fields = ("id",)
