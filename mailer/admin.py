from django.contrib import admin
from mailer.models import MailingRecipient, MailMessage, Mailing


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
