# app_users/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models

from app_materials.models import Course, Lesson

from .managers import UserManager

# вынес менеджер в managers.py согласно лучших практик кастомный менеджер необходим
# базовый менеджер ожидает наличие поля username и может вести себя неправильно.


class User(AbstractUser):
    """
    Кастомная модель пользователя.

    Наследуемся от AbstractUser, чтобы:
    - берём готовую реализацию аутентификации (пароль, группы, права, is_staff и т.д.);
    - но изменим главный идентификатор (username на email);
    - добавим свои поля (аватар, телефон, страна).
    """

    # Поле username из родительского AbstractUser нам больше не нужно.
    # Мы будем логиниться по email, поэтому отключаем username.
    username = None  # type: ignore[assignment]

    # Основное поле аутентификации.
    email = models.EmailField(
        unique=True,  # Поле email станет уникальным.
        verbose_name="Email",  # Человеко‑читаемое имя поля (для админки и форм).
    )

    # Дополнительные поля модели пользователя.

    # Аватар пользователя (фотография).
    avatar = models.ImageField(
        upload_to="users/",  # Файлы будут сохраняться в MEDIA_ROOT / "users/"
        blank=True,  # Поле НЕобязательно в формах (можно не загружать картинку).
        null=True,  # В БД поле может быть NULL (нет файла).
        verbose_name="Аватарка",  # Название поля в админке.
        help_text="Загрузи фото",  # Подсказка под полем в формах/админке.
    )

    # Номер телефона пользователя.
    phone = models.CharField(
        max_length=35,  # Максимальная длина строки в БД.
        verbose_name="Телефон",  # Название поля в админке/формах.
        blank=True,  # Поле необязательно (можно оставить пустым).
        # null=True не используем для CharField:
        # пустое значение храним как "" (пустую строку), а не как NULL —
        # так проще писать фильтры и логику.
        help_text="Введите номер телефона",
    )

    # Город пользователя.
    city = models.CharField(
        max_length=20,
        verbose_name="Город",
        blank=True,  # Можно не указывать страну.
        # null=False по умолчанию -> в БД будет храниться "" для пустого значения.
    )

    token = models.CharField(
        max_length=100,
        verbose_name="Токен",
        blank=True,
    )

    # Настройки аутентификации Django.

    # Говорим Django, что теперь "имя пользователя" (логин) — это email.
    # Используется:
    # - в аутентификации (authenticate)
    # - в createsuperuser (какое поле спрашивать как логин)
    USERNAME_FIELD = "email"

    # Список полей, которые будут дополнительно спрошены при createsuperuser,
    # помимо USERNAME_FIELD и пароля.
    # Здесь оставляем пустой список — достаточно email + password.
    REQUIRED_FIELDS = []

    # Подключаем свой менеджер, который:
    # - умеет создавать пользователей по email (create_user);
    # - умеет создавать суперпользователей без username (create_superuser).
    objects = UserManager()  # type: ignore[misc, assignment]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["email"]

    def __str__(self):
        """
        Строковое представление объекта пользователя.

        Возвращаем email, чтобы в админке и консоли пользователи отображались
        понятным образом, а не "User object (1)".
        """
        return self.email


class Payment(models.Model):
    CASH = "cash"
    TRANSFER = "transfer"

    PAYMENT_METHOD_CHOICES = [
        (CASH, "Наличные"),
        (TRANSFER, "Перевод на счет"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name="пользователь",
    )

    paid_course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="course_payments",
        verbose_name="оплаченный курс",
    )

    paid_lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="lesson_payments",
        verbose_name="отдельно оплаченный урок",
    )

    amount = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name="сумма оплаты",
    )

    payment_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="дата оплаты",
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        verbose_name="способ оплаты",
    )

    class Meta:
        verbose_name = "платеж"
        verbose_name_plural = "платежи"

    def __str__(self):
        return f"{self.user} - {self.amount} ({self.payment_method})"
