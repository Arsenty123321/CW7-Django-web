from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from users.apps import UsersConfig
from users.views import UserCreateView, email_verification, PasswordResetRequestView, PasswordResetConfirmView, \
    UserProfileDetailView, UserProfileUpdateView

app_name = UsersConfig.name

urlpatterns = [
    path("login/", LoginView.as_view(template_name="users/login.html"), name="login"),
    path('logout/', LogoutView.as_view(next_page=''), name='logout'),
    path("register/", UserCreateView.as_view(), name="register"),
    path("email-confirm/<str:token>/", email_verification, name="email-confirm"),
    path('password-reset-request/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path("profile/", UserProfileDetailView.as_view(), name="profile_detail"),
    path("profile/edit/", UserProfileUpdateView.as_view(), name="profile_edit"),
]
