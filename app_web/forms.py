# app_web/forms.py

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError

from app_materials.models import Course, Lesson
from app_materials.validators import validate_video_url
from app_users.permissions import is_moderator

User = get_user_model()


class BootstrapFormMixin:
    """Добавляет Bootstrap-классы всем полям формы."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs.setdefault("class", "form-check-input")
            elif isinstance(widget, (forms.Select, forms.SelectMultiple)):
                widget.attrs.setdefault("class", "form-select")
            else:
                widget.attrs.setdefault("class", "form-control")


class EmailAuthenticationForm(BootstrapFormMixin, AuthenticationForm):
    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"autofocus": True, "autocomplete": "email", "placeholder": "you@example.com"}),
    )
    password = forms.CharField(
        label="Пароль",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password", "placeholder": "Пароль"}),
    )


class RegisterForm(BootstrapFormMixin, forms.ModelForm):
    field_order = ("email", "phone", "city", "avatar", "password1", "password2")

    password1 = forms.CharField(
        label="Пароль",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text="Минимум 8 символов, не только цифры.",
    )
    password2 = forms.CharField(
        label="Повторите пароль",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )

    class Meta:
        model = User
        fields = ("email", "phone", "city", "avatar")
        labels = {"email": "Email", "phone": "Телефон", "city": "Город", "avatar": "Аватар"}
        widgets = {"email": forms.EmailInput(attrs={"placeholder": "you@example.com"})}

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            self.add_error("password2", "Пароли не совпадают.")
            return cleaned_data

        if password1:
            user = User(email=cleaned_data.get("email") or "")
            try:
                validate_password(password1, user)
            except ValidationError as error:
                self.add_error("password1", error)

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class ProfileForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ("email", "phone", "city", "avatar")
        labels = {"email": "Email", "phone": "Телефон", "city": "Город", "avatar": "Аватар"}


class CourseForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Course
        fields = ("name", "description", "preview")
        labels = {"name": "Название", "description": "Описание", "preview": "Обложка"}
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Например, Django REST Framework"}),
            "description": forms.Textarea(attrs={"rows": 5, "placeholder": "Чему посвящён курс"}),
        }


class LessonForm(BootstrapFormMixin, forms.ModelForm):
    video_url = forms.CharField(
        label="Ссылка на видео",
        max_length=255,
        widget=forms.URLInput(attrs={"placeholder": "https://youtube.com/watch?v=..."}),
        help_text="Разрешены YouTube и Rutube.",
    )

    class Meta:
        model = Lesson
        fields = ("course", "name", "description", "preview", "video_url")
        labels = {
            "course": "Курс",
            "name": "Название",
            "description": "Описание",
            "preview": "Обложка",
            "video_url": "Ссылка на видео",
        }
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Например, Введение в DRF"}),
            "description": forms.Textarea(attrs={"rows": 4, "placeholder": "О чём урок"}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        queryset = Course.objects.order_by("name")
        if user is not None and not is_moderator(user):
            queryset = queryset.filter(owner=user)
        self.fields["course"].queryset = queryset
        self.fields["course"].empty_label = "Выберите курс"

    def clean_video_url(self):
        value = self.cleaned_data["video_url"]
        try:
            return validate_video_url(value)
        except DRFValidationError as error:
            raise ValidationError(error.detail)
