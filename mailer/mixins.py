from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied


class OwnerRequiredMixin(LoginRequiredMixin):
    """
        Миксин для проверки, что текущий пользователь является владельцем объекта.
    """

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        user = self.request.user

        # Проверить, принадлежит ли объект текущему пользователю
        if obj.owner != user:
            raise PermissionDenied(f"Доступ запрещен: {user} != {obj.owner}")
        return obj


class OwnerManagersRequiredMixin(LoginRequiredMixin):
    """
        Миксин для проверки, что текущий пользователь является владельцем объекта
        или у пользователя присутствует группа mailing_manager.
    """

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        user = self.request.user

        # Проверить, принадлежит ли объект текущему пользователю
        if obj.owner != user and not user.groups.filter(name='mailing_manager').exists():
            raise PermissionDenied(
                f"Доступ запрещен: Вы не владелец объекта, привилегии менеджера отсутствуют - {user} != {obj.owner}")
        return obj
