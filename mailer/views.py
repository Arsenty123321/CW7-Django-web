from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView

from mailer.forms import MailingForm
from mailer.models import Mailing


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
    #    template_name = "blog/blog_form.html"
    #    fields = ("title", "content", "preview")
    form_class = MailingForm

    # field_to_exclude = ("status", "owner")

    success_url = reverse_lazy("mailer:mailing_list")

    def form_valid(self, form):
        user = self.request.user
        form.instance.owner = user
        return super().form_valid(form)


class MailingUpdateView(LoginRequiredMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    #template_name = "mailer/mailing_form.html"
    #fields = ("title", "content", "preview")
    #field_to_exclude = ("status", "owner")
    success_url = reverse_lazy("mailer:mailing_list")

    def get_success_url(self):
        return reverse("mailer:mailing_detail", args=[self.kwargs.get("pk")])


class MailingDeleteView(LoginRequiredMixin, DeleteView):
    model = Mailing
    context_object_name = "mailing"
    success_url = reverse_lazy("mailer:mailing_list")
