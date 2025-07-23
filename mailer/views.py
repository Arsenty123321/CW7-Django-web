from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView

from mailer.forms import MailingForm, MailingDisableForm
from mailer.mixins import OwnerRequiredMixin, OwnerManagersRequiredMixin
from mailer.models import Mailing, MailMessage, MailingRecipient
from mailer.services import get_user_stats, get_mailings_stats, get_general_stats, send_mailing, set_mailing_status, \
    remove_messages_cache_from_user, get_messages_from_cache_from_user, get_recipients_from_cache_from_user, \
    remove_recipients_cache_from_user


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

    def get_queryset(self):
        if self.request.user.groups.filter(name="mailing_manager").exists():
            return Mailing.objects.all()
        return Mailing.objects.filter(owner=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_manager"] = self.request.user.groups.filter(name="mailing_manager").exists()
        return context


class MailingDetailView(OwnerManagersRequiredMixin, DetailView):
    model = Mailing
    context_object_name = "mailing"


class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    success_url = reverse_lazy("mailer:mailing_list")

    def get_form_kwargs(self):
        kwargs = super(MailingCreateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MailingUpdateView(OwnerRequiredMixin, UpdateView):
    model = Mailing
    form_class = MailingForm

    def get_form_kwargs(self):
        kwargs = super(MailingUpdateView, self).get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse("mailer:mailing_detail", args=[self.kwargs.get("pk")])


class MailingDisableView(LoginRequiredMixin, UpdateView):
    model = Mailing
    form_class = MailingDisableForm
    success_url = reverse_lazy("mailer:mailing_list")

    def dispatch(self, request, *args, **kwargs):
        if not request.user.groups.filter(name="mailing_manager").exists():
            raise PermissionDenied("У вас нет прав доступа к этой странице.")
        return super().dispatch(request, *args, **kwargs)


class MailingDeleteView(OwnerRequiredMixin, DeleteView):
    model = Mailing
    context_object_name = "mailing"
    success_url = reverse_lazy("mailer:mailing_list")


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


class MailingDetailStatsView(OwnerManagersRequiredMixin, DetailView):
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


class MessageListView(LoginRequiredMixin, ListView):
    model = MailMessage
    context_object_name = 'messages'
    template_name = "mailer/message_list.html"

    def get_queryset(self):
        if self.request.user.groups.filter(name="mailing_manager").exists():
            return MailMessage.objects.all()

        # Кешируем объекты пользователя
        queryset = get_messages_from_cache_from_user(self.request.user)
        return queryset


class MessageDetailView(OwnerManagersRequiredMixin, DetailView):
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
        # Удаляем кэш сообщений пользователя, когда создаем новое сообщение
        remove_messages_cache_from_user(user)
        return super().form_valid(form)


class MessageUpdateView(OwnerRequiredMixin, UpdateView):
    model = MailMessage
    fields = ("title", "content")
    template_name = "mailer/message_form.html"

    def form_valid(self, form):
        user = self.request.user
        # Удаляем кэш сообщений пользователя, когда изменяем сообщение
        remove_messages_cache_from_user(user)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("mailer:message_detail", args=[self.kwargs.get("pk")])


class MessageDeleteView(OwnerRequiredMixin, DeleteView):
    model = MailMessage
    context_object_name = "message"
    template_name = "mailer/message_confirm_delete.html"
    success_url = reverse_lazy("mailer:message_list")

    def form_valid(self, form):
        user = self.request.user
        # Удаляем кэш сообщений пользователя, когда удаляем сообщение
        remove_messages_cache_from_user(user)
        return super().form_valid(form)


class RecipientListView(LoginRequiredMixin, ListView):
    model = MailingRecipient
    context_object_name = 'recipients'
    template_name = "mailer/recipient_list.html"

    def get_queryset(self):
        if self.request.user.groups.filter(name="mailing_manager").exists():
            return MailingRecipient.objects.all()
        # Кешируем объекты пользователя
        queryset = get_recipients_from_cache_from_user(self.request.user)
        return queryset


class RecipientDetailView(OwnerManagersRequiredMixin, DetailView):
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
        # Удаляем кэш получателей пользователя, когда добавляем нового получателя
        remove_recipients_cache_from_user(user)
        return super().form_valid(form)


class RecipientUpdateView(OwnerRequiredMixin, UpdateView):
    model = MailingRecipient
    fields = ("email", "full_name", "comment")
    template_name = "mailer/recipient_form.html"

    def form_valid(self, form):
        user = self.request.user
        # Удаляем кэш получателей пользователя, когда изменяем получателя
        remove_recipients_cache_from_user(user)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("mailer:recipient_detail", args=[self.kwargs.get("pk")])


class RecipientDeleteView(OwnerRequiredMixin, DeleteView):
    model = MailingRecipient
    context_object_name = "recipient"
    template_name = "mailer/recipient_confirm_delete.html"
    success_url = reverse_lazy("mailer:recipient_list")

    def form_valid(self, form):
        user = self.request.user
        # Удаляем кэш получателей пользователя, когда удаляем получателя
        remove_recipients_cache_from_user(user)
        return super().form_valid(form)


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
