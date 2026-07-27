# app_materials/tasks.py

from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

from .models import Course, Subscription


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
    message = (
        f"Курс «{course.name}» был обновлён.\n\n"
        f"Зайдите в личный кабинет, чтобы посмотреть новые материалы."
    )

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
