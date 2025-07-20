import secrets

from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import SetPasswordForm
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy, reverse
from django.utils.crypto import get_random_string
from django.views import View
from django.views.generic import CreateView
from django.contrib import messages

from config.settings import EMAIL_HOST_USER
from .forms import UserRegisterForm
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
    user = get_object_or_404(User, token=token)
    user.is_active = True
    # Замена использованного токена новым (неизвестным)
    user.token = secrets.token_hex(32)
    user.save()
    return redirect(reverse("users:login"))


class PasswordResetRequestView(View):
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
