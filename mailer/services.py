from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.utils import timezone

from config.settings import EMAIL_HOST_USER

from mailer.models import Mailing, MailingAttempt, MailingRecipient


def validate_mailing(mailing):
    """
        Проверка времени и статуса у рассылки
    """
    cur_time = timezone.now()

    if mailing.start_datetime and cur_time < mailing.start_datetime:
        raise ValidationError("Время рассылки еще не наступило")

    if mailing.end_datetime and cur_time > mailing.end_datetime:
        mailing.status = "Completed"
        mailing.save()
        raise ValidationError(f"Время рассылки окончено - статус рассылки изменен на \"Завершена\" | "
                              f"ID:{mailing.id} - {mailing.message.title}")

    if mailing.is_disabled:
        mailing.status = "Completed"
        mailing.save()
        raise ValidationError("Рассылка отключена менеджером - статус рассылки изменен на \"Завершена\" | "
                              f"ID:{mailing.id} - {mailing.message.title}")

    if mailing.status != "Launched":
        mailing.status = "Launched"
        if not mailing.start_datetime:
            mailing.start_datetime = cur_time
        mailing.save()


def update_status_by_lifetime(mailing):
    """
        Изменение статуса рассылки исходя из времени окончания рассылки
    """

    cur_time = timezone.now()

    if mailing.end_datetime and cur_time > mailing.end_datetime:
        mailing.status = "Completed"
        mailing.save()


def set_mailing_status(mailing_id, status):
    """
        Изменение статуса рассылки
    """

    mailing = Mailing.objects.get(pk=mailing_id)
    mailing.status = status
    mailing.save()


def send_mailing(mailing_id):
    """
        Отправка рассылки
    """

    mailing = Mailing.objects.get(pk=mailing_id)
    validate_mailing(mailing)

    for recipient in mailing.recipient.all():
        send_email(mailing, recipient)

    # mailing.status = "Completed"
    # mailing.save()


def send_email(mailing, recipient):
    """
        Отправляет письмо одному получателю
    """

    if not recipient.email:
        raise ValueError("Не указан email получателя!")

    mailing_id = mailing.id
    subject = mailing.message.title
    message = mailing.message.content
    from_email = EMAIL_HOST_USER
    recipient_list = [recipient.email]

    try:
        cur_time = timezone.now()
        send_mail(subject, message, from_email, recipient_list)
        # Логирование
        MailingAttempt.objects.create(mailing=mailing, attempt_status="Success",
                                      answer=f"Отправлено получателю [{cur_time}]: {recipient.email} - Ok")
        print(f"Рассылка[Id]={mailing_id}: Письмо отправлено получателю [{cur_time}]: {recipient.email}")
    except Exception as e:
        # Логирование
        MailingAttempt.objects.create(mailing=mailing, attempt_status="Failed",
                                      answer=f"Ошибка отправки [{cur_time}]: {recipient.email} {mailing.pk}: {e}")
        print(f"Рассылка[Id]={mailing_id}: Ошибка отправки [{cur_time}]: {recipient.email} {mailing.pk}: {e}")


def get_user_stats(user):
    """
        Статистика попыток по пользователю
    """

    attempt = MailingAttempt.objects.filter(mailing__owner=user)
    total = attempt.count()
    success = attempt.filter(attempt_status="Success").count()

    return {
        "total": total,
        "success": success,
        "failed": total - success,
        "success_rate": (success / total * 100) if total > 0 else 0,
    }


def get_mailings_stats(mailing):
    """
        Статистика по рассылке
    """

    attempt = MailingAttempt.objects.filter(mailing=mailing)
    total = attempt.count()
    success = attempt.filter(attempt_status="Success").count()
    server_answers = attempt.values_list('answer', flat=True)

    return {
        "total": total,
        "success": success,
        "failed": total - success,
        "success_rate": (success / total * 100) if total > 0 else 0,
        "server_answers": server_answers,
    }


def get_general_stats():
    """
        Общая статистика сервиса
    """

    mailing_total = Mailing.objects.all().count()
    mailing_launched = Mailing.objects.filter(status='Launched').count()
    mailing_recipient_total = MailingRecipient.objects.all().count()

    return {
        "mailing_total": mailing_total,
        "mailing_launched": mailing_launched,
        "mailing_recipient_total": mailing_recipient_total,
    }
