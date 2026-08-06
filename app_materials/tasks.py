# app_materials/tasks.py

import datetime

from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils import timezone

from .models import Course, Subscription

User = get_user_model()


@shared_task
def send_course_update_email_task(course_id: int):
    """
    Рассылка писем всем пользователям, подписанным на указанный курс.
    """
    try:
        course = Course.objects.get(pk=course_id)
    except Course.DoesNotExist:
        return

    # Все подписчики курса.
    subscriptions = Subscription.objects.filter(course=course).select_related("user")

    if not subscriptions.exists():
        return

    subject = f"Обновление материалов курса: {course.name}"
    message = f"Курс «{course.name}» был обновлён.\n\n" f"Зайдите в личный кабинет, чтобы посмотреть новые материалы."

    recipient_list = [sub.user.email for sub in subscriptions if sub.user.email]

    if not recipient_list:
        return

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipient_list,
        fail_silently=False,
    )


@shared_task
def deactivate_inactive_users_task():
    """
    Находит пользователей, которые не заходили более месяца,
    и отключает их (is_active = False).
    """
    now = timezone.now()
    one_month_ago = now - datetime.timedelta(days=30)

    # Пользователи, у которых last_login указан и он старше месяца,
    # и они ещё активны.
    users_qs = User.objects.filter(
        is_active=True,
        last_login__isnull=False,
        last_login__lt=one_month_ago,
    )

    # Если нужно игнорировать суперпользователей/модераторов,
    # можно добавить фильтры: is_superuser=False, is_staff=False и т.п.
    users_qs.update(is_active=False)
