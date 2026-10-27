from django.core.management.base import BaseCommand
from django.utils import timezone
from django_celery_beat.models import IntervalSchedule, PeriodicTask


class Command(BaseCommand):
    help = (
        "Создаёт или обновляет периодическую задачу "
        "для блокировки неактивных пользователей "
        "(app_materials.tasks.deactivate_inactive_users_task)."
    )

    def handle(self, *args, **options):
        # Интервал: раз в день.
        schedule, _ = IntervalSchedule.objects.get_or_create(
            every=1,
            period=IntervalSchedule.DAYS,
        )

        # Периодическая задача.
        task_name = "Deactivate inactive users"
        task_path = "app_materials.tasks.deactivate_inactive_users_task"

        periodic_task, created = PeriodicTask.objects.update_or_create(
            name=task_name,
            defaults={
                "interval": schedule,
                "task": task_path,
                "enabled": True,
                # Можно задать время старта, иначе начнёт сразу.
                "start_time": timezone.now(),
                "one_off": False,
            },
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f"Создана задача: {task_name}"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Обновлена задача: {task_name}"))
