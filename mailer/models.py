from django.contrib.auth.models import User
from django.db import models


class MailingRecipient(models.Model):
    email = models.EmailField(unique=True, verbose_name="Email")
    full_name = models.CharField(max_length=100, verbose_name="Ф.И.О.", help_text="Введите Ф.И.О. получателя")
    comment = models.TextField(verbose_name="Комментарий", help_text="Введите комментарий")

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        help_text="Укажите пользователя",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Получатель рассылки"
        verbose_name_plural = "Получатели рассылок"
        ordering = ["id"]

    def __str__(self):
        return self.email


class MailMessage(models.Model):
    title = models.CharField(max_length=50, verbose_name="Тема письма", help_text="Введите тему письма")
    content = models.TextField(verbose_name="Тело письма", help_text="Введите текст письма")

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        help_text="Укажите пользователя",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        ordering = ["id"]

    def __str__(self):
        return self.title


class Mailing(models.Model):
    start_datetime = models.DateTimeField(verbose_name="Дата и время первой отправки",
                                          help_text="Введите дату и время первой отправки")
    end_datetime = models.DateTimeField(verbose_name="Дата и время окончания отправки",
                                        help_text="Введите дату и время окончания отправки")
    STATUS_CHOICES = [
        ('Created', 'Создана'),
        ('Running', 'Запущена'),
        ('Completed', 'Завершена'),
    ]
    status = models.CharField(max_length=10,
                              choices=STATUS_CHOICES,
                              default='Created',
                              verbose_name="Статус",
                              help_text="Статус рассылки")
    message = models.ForeignKey(MailMessage, on_delete=models.CASCADE)
    recipient = models.ManyToManyField(MailingRecipient, verbose_name="Получатели")
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        help_text="Укажите пользователя",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"
        ordering = ["id"]

    def __str__(self):
        return f"Сообщение:{self.message}, статус:{self.status}"
