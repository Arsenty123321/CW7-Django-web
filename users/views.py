import secrets

from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy, reverse
from django.utils.crypto import get_random_string
from django.views import View
from django.views.generic import CreateView, ListView, DetailView, UpdateView
from django.contrib import messages

from config.settings import EMAIL_HOST_USER
from .forms import UserRegisterForm, UserProfileForm
from .models import User


class UserCreateView(CreateView):
    model = User
    form_class = UserRegisterForm
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        token = secrets.token_hex(16)
        user.token = token
        user.save()

        host = self.request.get_host()
        url = f"http://{host}/users/email-confirm/{token}/"

        send_mail(
            subject="Подтверждение почты",
            message=f"Привет, перейди по ссылке для подтверждения почты {url}",
            from_email=EMAIL_HOST_USER,
            recipient_list=[user.email]
        )
        return super().form_valid(form)


def email_verification(request, token):
    """
        Подтверждение почты пользователя
    """

    user = get_object_or_404(User, token=token)
    user.is_active = True
    # Замена использованного токена новым (неизвестным)
    user.token = secrets.token_hex(32)
    user.save()
    return redirect(reverse("users:login"))


class PasswordResetRequestView(View):
    """
        Запрос на восстановление пароля, на почту отправляется временный пароль
    """

    def get(self, request):
        return render(request, 'users/password_reset_request_form.html')

    def post(self, request):
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, 'Пользователь с таким email не найден.')
            return redirect('users:password_reset_request')

        temp_password = get_random_string(length=10)
        user.set_password(temp_password)
        user.save()

        send_mail(
            subject="Временный пароль для восстановления",
            message=f"Ваш временный пароль для восстановления: {temp_password}",
            from_email=EMAIL_HOST_USER,
            recipient_list=[user.email],
        )

        messages.success(request, 'На ваш email отправлен временный пароль для восстановления.')
        return redirect('users:password_reset_confirm')


class PasswordResetConfirmView(View):
    """
        Подтверждение сброса и установка нового пароля
    """

    def get(self, request):
        form = SetPasswordForm(request.user)
        return render(request, 'users/password_reset_confirm_form.html', {'form': form})

    def post(self, request):
        email = request.POST.get('email')
        temp_password = request.POST.get('temp_password')
        new_password = request.POST.get('new_password')

        user = authenticate(request, email=email, password=temp_password)
        if user is not None:
            user.set_password(new_password)
            user.save()
            login(request, user)
            messages.success(request, 'Пароль успешно изменен.')
            return redirect('mailer:home')
        else:
            messages.error(request, 'Неверный временный пароль.')
            return redirect('users:password_reset_confirm')


# class UserListView(LoginRequiredMixin, ListView):
#     """
#         Список пользователей для просмотра менеджером
#     """
#
#     model = User
#     template_name = "users/user_list.html"
#     context_object_name = "users"
#
#     def get_queryset(self):
#         #        if not is_manager(self.request.user):
#         #            return HttpResponseForbidden('Доступ запрещен', status=403)
#         return User.objects.all().order_by("id")
#
#     def dispatch(self, request, *args, **kwargs):
#         if not request.user.groups.filter(name="mailing_manager").exists():
#             # raise PermissionDenied("У вас нет прав доступа к этой странице.")
#             return HttpResponseForbidden('У вас нет прав на просмотр этого списка')
#         return super().dispatch(request, *args, **kwargs)


class UserProfileDetailView(LoginRequiredMixin, DetailView):
    """
        Просмотр собственного профиля
    """

    model = User
    template_name = "users/profile.html"
    context_object_name = "user"

    def get_object(self):
        return self.request.user  # Возвращает текущего авторизованного пользователя


class UserProfileUpdateView(LoginRequiredMixin, UpdateView):
    """
        Редактирование собственного профиля
    """

    model = User
    form_class = UserProfileForm
    template_name = "users/profile_edit.html"
    success_url = reverse_lazy("users:profile_detail")

    def get_object(self):
        return self.request.user
