from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView

from mailer.forms import MailingForm
from mailer.mixins import OwnerRequiredMixin
from mailer.models import Mailing, MailMessage, MailingRecipient
from mailer.services import get_user_stats, get_mailings_stats, get_general_stats, send_mailing, set_mailing_status


class HomeTemplateView(TemplateView):
    template_name = "mailer/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Общая статистика сервиса
        context["general_stats"] = get_general_stats()
        return context


class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    context_object_name = 'mailings'


class MailingDetailView(OwnerRequiredMixin, DetailView):
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


class MailingUpdateView(OwnerRequiredMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    success_url = reverse_lazy("mailer:mailing_list")

    def get_success_url(self):
        return reverse("mailer:mailing_detail", args=[self.kwargs.get("pk")])


class MailingDeleteView(OwnerRequiredMixin, DeleteView):
    model = Mailing
    context_object_name = "mailing"
    success_url = reverse_lazy("mailer:mailing_list")


class MessageListView(LoginRequiredMixin, ListView):
    model = MailMessage
    context_object_name = 'messages'
    template_name = "mailer/message_list.html"


class MessageDetailView(OwnerRequiredMixin, DetailView):
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


class MessageUpdateView(OwnerRequiredMixin, UpdateView):
    model = MailMessage
    fields = ("title", "content")
    template_name = "mailer/message_form.html"
    success_url = reverse_lazy("mailer:message_list")

    def get_success_url(self):
        return reverse("mailer:message_detail", args=[self.kwargs.get("pk")])


class MessageDeleteView(OwnerRequiredMixin, DeleteView):
    model = MailMessage
    context_object_name = "message"
    template_name = "mailer/message_confirm_delete.html"
    success_url = reverse_lazy("mailer:message_list")


class RecipientListView(LoginRequiredMixin, ListView):
    model = MailingRecipient
    context_object_name = 'recipients'
    template_name = "mailer/recipient_list.html"


class RecipientDetailView(OwnerRequiredMixin, DetailView):
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


class RecipientUpdateView(OwnerRequiredMixin, UpdateView):
    model = MailingRecipient
    fields = ("email", "full_name", "comment")
    template_name = "mailer/recipient_form.html"
    success_url = reverse_lazy("mailer:recipient_list")

    def get_success_url(self):
        return reverse("mailer:recipient_detail", args=[self.kwargs.get("pk")])


class RecipientDeleteView(OwnerRequiredMixin, DeleteView):
    model = MailingRecipient
    context_object_name = "recipient"
    template_name = "mailer/recipient_confirm_delete.html"
    success_url = reverse_lazy("mailer:recipient_list")


class MailingStatsView(LoginRequiredMixin, TemplateView):
    template_name = "mailer/mailing_stats.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Общая статистика пользователя
        user_stats = get_user_stats(user)

        context.update({
            "user_stats": user_stats,
        })
        return context


class MailingDetailStatsView(OwnerRequiredMixin, DetailView):
    model = Mailing
    context_object_name = "mailing"
    template_name = "mailer/mailing_detail_stats.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mailing = self.object

        # Детальная статистика по рассылке
        mailing_stats = get_mailings_stats(mailing)

        context.update({
            "mailing_stats": mailing_stats,
        })
        return context


@login_required
def mailing_run_view(request, pk):
    mailing = get_object_or_404(Mailing, id=pk)
    if request.user != mailing.owner:
        raise PermissionDenied("У вас нет прав доступа к этому объекту.")

    try:
        send_mailing(mailing.id)
        messages.success(request, f"Рассылка [{mailing.id}] успешно запущена", "success")
    except Exception as e:
        messages.error(request, str(e), "danger")
    finally:
        # Перенаправление на страницу рассылок
        return redirect(request.META.get('HTTP_REFERER', reverse('mailer:mailing_list')))


@login_required
def mailing_launch_view(request, pk):
    mailing = get_object_or_404(Mailing, id=pk)
    if request.user != mailing.owner:
        raise PermissionDenied("У вас нет прав доступа к этому объекту.")
    set_mailing_status(pk, "Launched")
    return redirect(request.META.get('HTTP_REFERER', reverse('mailer:mailing_list')))


@login_required
def mailing_complete_view(request, pk):
    mailing = get_object_or_404(Mailing, id=pk)
    if request.user != mailing.owner:
        raise PermissionDenied("У вас нет прав доступа к этому объекту.")
    set_mailing_status(pk, "Completed")
    return redirect(request.META.get('HTTP_REFERER', reverse('mailer:mailing_list')))
