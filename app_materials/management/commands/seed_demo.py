# app_materials/management/commands/seed_demo.py

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django.db import transaction

from app_materials.models import Course, Lesson, Subscription
from app_users.models import Payment

User = get_user_model()

DEMO_PASSWORD = "DemoPass123!"

COURSES = [
    {
        "name": "Python с нуля",
        "description": "Синтаксис, функции, коллекции и ООП. Практика на небольших задачах без магии.",
        "lessons": [
            ("Переменные и типы данных", "Разбираем строки, числа и приведение типов."),
            ("Списки, кортежи и словари", "Основные операции и когда что выбирать."),
            ("Функции и модули", "Аргументы, возвращаемые значения и структура проекта."),
        ],
    },
    {
        "name": "Django REST Framework",
        "description": "Сериализаторы, ViewSet, права доступа, JWT и документирование API через OpenAPI.",
        "lessons": [
            ("Сериализаторы и валидация", "Как DRF превращает модели в JSON и проверяет данные."),
            ("ViewSet и маршрутизация", "CRUD без дублирования кода."),
            ("Права доступа", "Владелец объекта, модератор и обычный пользователь."),
        ],
    },
    {
        "name": "SQL и PostgreSQL",
        "description": "Запросы, JOIN, индексы, транзакции и типичные ошибки при работе с базой.",
        "lessons": [
            ("SELECT и фильтрация", "WHERE, ORDER BY, LIMIT и агрегаты."),
            ("JOIN и связи таблиц", "INNER, LEFT и как не получить декартово произведение."),
            ("Индексы и EXPLAIN", "Как читать план запроса и ускорять выборки."),
        ],
    },
    {
        "name": "Docker и Docker Compose",
        "description": "Контейнеры, образы, тома и запуск Django с PostgreSQL и Redis одной командой.",
        "lessons": [
            ("Образы и контейнеры", "Чем Dockerfile отличается от docker-compose.yml."),
            ("Compose для Django", "Web, база, Redis и переменные окружения."),
            ("Полезные команды", "Логи, пересборка, очистка и отладка."),
        ],
    },
    {
        "name": "Git для командной работы",
        "description": "Ветки, коммиты, pull request и разрешение конфликтов на практике.",
        "lessons": [
            ("Ветки и коммиты", "Как вести историю, которую приятно читать."),
            ("Merge и rebase", "Когда что использовать и как не сломать ветку."),
            ("Pull request", "Ревью, исправления и чистое слияние."),
        ],
    },
    {
        "name": "Linux для разработчика",
        "description": "Терминал, права, процессы, systemd и базовое администрирование сервера.",
        "lessons": [
            ("Файлы и права", "chmod, chown и почему 755 — не всегда ответ."),
            ("Процессы и порты", "ps, top, ss и поиск занятого порта."),
            ("systemd и логи", "Запуск сервиса и чтение journalctl."),
        ],
    },
]


class Command(BaseCommand):
    help = "Создаёт демонстрационные курсы, уроки, платежи и аккаунты."

    @transaction.atomic
    def handle(self, *args, **options):
        moderators, _ = Group.objects.get_or_create(name="moderators")

        student = self._upsert_user("student@example.com", city="Москва")
        teacher = self._upsert_user("teacher@example.com", city="Санкт-Петербург")
        moderator = self._upsert_user("moderator@example.com", city="Казань")
        moderator.groups.add(moderators)

        admin = self._upsert_user("admin@example.com", city="Москва")
        admin.is_staff = True
        admin.is_superuser = True
        admin.save(update_fields=["is_staff", "is_superuser"])

        courses = []
        for course_data in COURSES:
            course, _ = Course.objects.update_or_create(
                name=course_data["name"],
                defaults={
                    "description": course_data["description"],
                    "owner": teacher,
                },
            )
            courses.append(course)

            for index, (lesson_name, lesson_description) in enumerate(course_data["lessons"], start=1):
                Lesson.objects.update_or_create(
                    course=course,
                    name=lesson_name,
                    defaults={
                        "description": lesson_description,
                        "video_url": f"https://youtube.com/watch?v=demo{index}",
                        "owner": teacher,
                    },
                )

        Subscription.objects.get_or_create(user=student, course=courses[0])
        Subscription.objects.get_or_create(user=student, course=courses[1])

        Payment.objects.get_or_create(
            user=student,
            paid_course=courses[0],
            amount="4900.00",
            payment_method=Payment.STRIPE,
        )
        Payment.objects.get_or_create(
            user=student,
            paid_course=courses[1],
            amount="3900.00",
            payment_method=Payment.TRANSFER,
        )

        self.stdout.write(self.style.SUCCESS("Demo data is ready."))
        self.stdout.write("  student@example.com / DemoPass123!")
        self.stdout.write("  teacher@example.com / DemoPass123!")
        self.stdout.write("  moderator@example.com / DemoPass123!")
        self.stdout.write("  admin@example.com / DemoPass123!  (superuser)")

    def _upsert_user(self, email, city):
        user, _ = User.objects.get_or_create(email=email, defaults={"city": city})
        user.city = city
        user.set_password(DEMO_PASSWORD)
        user.is_active = True
        user.save(update_fields=["password", "is_active", "city"])
        return user
