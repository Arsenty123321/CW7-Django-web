from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView

from mailer.forms import MailingForm
from mailer.models import Mailing, MailMessage, MailingRecipient


class HomeTemplateView(TemplateView):
    template_name = "mailer/index.html"


class MailingListView(ListView):
    model = Mailing
    context_object_name = 'mailings'


class MailingDetailView(LoginRequiredMixin, DetailView):
    model = Mailing
    context_object_name = "mailing"


class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    success_url = reverse_lazy("mailer:mailing_list")

    def form_valid(self, form):
        user = self.request.user
        form.instance.owner = user
        return super().form_valid(form)


class MailingUpdateView(LoginRequiredMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    success_url = reverse_lazy("mailer:mailing_list")

    def get_success_url(self):
        return reverse("mailer:mailing_detail", args=[self.kwargs.get("pk")])


class MailingDeleteView(LoginRequiredMixin, DeleteView):
    model = Mailing
    context_object_name = "mailing"
    success_url = reverse_lazy("mailer:mailing_list")


# AAAAAAAAAAAAAAAAAAAAAA

class MessageListView(ListView):
    model = MailMessage
    context_object_name = 'messages'
    template_name = "mailer/message_list.html"


class MessageDetailView(LoginRequiredMixin, DetailView):
    model = MailMessage
    context_object_name = "message"
    template_name = "mailer/message_detail.html"


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = MailMessage
    fields = ("title", "content")
    template_name = "mailer/message_form.html"
    success_url = reverse_lazy("mailer:message_list")

    def form_valid(self, form):
        user = self.request.user
        form.instance.owner = user
        return super().form_valid(form)


class MessageUpdateView(LoginRequiredMixin, UpdateView):
    model = MailMessage
    fields = ("title", "content")
    template_name = "mailer/message_form.html"
    success_url = reverse_lazy("mailer:message_list")

    def get_success_url(self):
        return reverse("mailer:message_detail", args=[self.kwargs.get("pk")])


class MessageDeleteView(LoginRequiredMixin, DeleteView):
    model = MailMessage
    context_object_name = "message"
    template_name = "mailer/message_confirm_delete.html"
    success_url = reverse_lazy("mailer:message_list")

# ##### BBBBBBBBBBBBB
#
class RecipientListView(ListView):
    model = MailingRecipient
    context_object_name = 'recipients'
    template_name = "mailer/recipient_list.html"


class RecipientDetailView(LoginRequiredMixin, DetailView):
    model = MailingRecipient
    context_object_name = "recipient"
    template_name = "mailer/recipient_detail.html"


class RecipientCreateView(LoginRequiredMixin, CreateView):
    model = MailingRecipient
    fields = ("email", "full_name", "comment")
    template_name = "mailer/recipient_form.html"
    success_url = reverse_lazy("mailer:recipient_list")

    def form_valid(self, form):
        user = self.request.user
        form.instance.owner = user
        return super().form_valid(form)


class RecipientUpdateView(LoginRequiredMixin, UpdateView):
    model = MailingRecipient
    fields = ("email", "full_name", "comment")
    template_name = "mailer/recipient_form.html"
    success_url = reverse_lazy("mailer:recipient_list")

    def get_success_url(self):
        return reverse("mailer:recipient_detail", args=[self.kwargs.get("pk")])


class RecipientDeleteView(LoginRequiredMixin, DeleteView):
    model = MailingRecipient
    context_object_name = "recipient"
    template_name = "mailer/recipient_confirm_delete.html"
    success_url = reverse_lazy("mailer:recipient_list")