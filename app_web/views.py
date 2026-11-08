# app_web/views.py

from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView
from django.db.models import Count, Q, Sum
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, FormView, ListView, UpdateView

from app_materials.models import Course, Lesson, Subscription
from app_users.models import Payment
from app_users.permissions import is_moderator

from .forms import (
    CourseForm,
    EmailAuthenticationForm,
    LessonForm,
    ProfileForm,
    RegisterForm,
)

User = get_user_model()


class NotModeratorRequiredMixin(UserPassesTestMixin):
    """Создавать курсы и уроки могут только обычные пользователи."""

    def test_func(self):
        return not is_moderator(self.request.user)


class OwnerOrModeratorRequiredMixin(UserPassesTestMixin):
    """Редактировать объект могут владелец и модератор."""

    def test_func(self):
        obj = self.get_object()
        return is_moderator(self.request.user) or obj.owner_id == self.request.user.id


class OwnerOnlyRequiredMixin(UserPassesTestMixin):
    """Удалять объект может только владелец, модератор исключён."""

    def test_func(self):
        obj = self.get_object()
        return not is_moderator(self.request.user) and obj.owner_id == self.request.user.id


class EmailLoginView(LoginView):
    template_name = "app_web/login.html"
    authentication_form = EmailAuthenticationForm
    redirect_authenticated_user = True


class RegisterView(FormView):
    template_name = "app_web/register.html"
    form_class = RegisterForm
    success_url = reverse_lazy("app_web:home")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("app_web:home")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, f"Добро пожаловать, {user.email}!")
        return super().form_valid(form)


class CourseListView(ListView):
    """Каталог курсов: доступен без авторизации."""

    model = Course
    template_name = "app_web/course_list.html"
    context_object_name = "courses"
    paginate_by = 9

    def get_queryset(self):
        queryset = Course.objects.select_related("owner").annotate(lessons_total=Count("lessons")).order_by("name")
        query = self.request.GET.get("q", "").strip()
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) | Q(description__icontains=query) | Q(owner__email__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "").strip()
        context["can_create_course"] = self.request.user.is_authenticated and not is_moderator(self.request.user)
        return context


class CourseDetailView(DetailView):
    model = Course
    template_name = "app_web/course_detail.html"
    context_object_name = "course"

    def get_queryset(self):
        return Course.objects.select_related("owner").prefetch_related("lessons")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.object
        user = self.request.user

        moderator = user.is_authenticated and is_moderator(user)
        owner = user.is_authenticated and course.owner_id == user.id

        context["lessons"] = course.lessons.order_by("id")
        context["is_subscribed"] = (
            user.is_authenticated and Subscription.objects.filter(user=user, course=course).exists()
        )
        context["is_moderator"] = moderator
        context["can_manage"] = moderator or owner
        context["can_delete"] = owner and not moderator
        context["can_add_lesson"] = owner and not moderator
        return context


class SubscriptionToggleView(LoginRequiredMixin, View):
    """Подписка и отписка от курса через обычную HTML-форму."""

    def post(self, request, pk):
        course = get_object_or_404(Course, pk=pk)
        subscription, created = Subscription.objects.get_or_create(user=request.user, course=course)

        if created:
            messages.success(request, f"Вы подписались на курс «{course.name}».")
        else:
            subscription.delete()
            messages.info(request, f"Вы отписались от курса «{course.name}».")

        return redirect("app_web:course-detail", pk=course.pk)


class ProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileForm
    template_name = "app_web/profile.html"
    success_url = reverse_lazy("app_web:profile")

    def get_object(self, queryset=None):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_moderator"] = is_moderator(self.request.user)
        return context

    def form_valid(self, form):
        messages.success(self.request, "Профиль обновлён.")
        return super().form_valid(form)


class PaymentListView(LoginRequiredMixin, ListView):
    """Свои платежи; модератор видит все."""

    model = Payment
    template_name = "app_web/payments.html"
    context_object_name = "payments"
    paginate_by = 10

    def get_queryset(self):
        queryset = Payment.objects.select_related("user", "paid_course", "paid_lesson").order_by("-payment_date")
        if is_moderator(self.request.user):
            return queryset
        return queryset.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_moderator"] = is_moderator(self.request.user)
        context["total_amount"] = self.get_queryset().aggregate(total=Sum("amount"))["total"] or 0
        return context


class CourseCreateView(LoginRequiredMixin, NotModeratorRequiredMixin, CreateView):
    model = Course
    form_class = CourseForm
    template_name = "app_web/course_form.html"

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, "Курс создан.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("app_web:course-detail", kwargs={"pk": self.object.pk})


class CourseUpdateView(LoginRequiredMixin, OwnerOrModeratorRequiredMixin, UpdateView):
    model = Course
    form_class = CourseForm
    template_name = "app_web/course_form.html"

    def form_valid(self, form):
        messages.success(self.request, "Курс обновлён.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("app_web:course-detail", kwargs={"pk": self.object.pk})


class CourseDeleteView(LoginRequiredMixin, OwnerOnlyRequiredMixin, DeleteView):
    model = Course
    template_name = "app_web/confirm_delete.html"
    success_url = reverse_lazy("app_web:home")

    def form_valid(self, form):
        messages.success(self.request, f"Курс «{self.object.name}» удалён.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["object_type"] = "курс"
        context["cancel_url"] = reverse("app_web:course-detail", kwargs={"pk": self.object.pk})
        return context


class LessonCreateView(LoginRequiredMixin, NotModeratorRequiredMixin, CreateView):
    model = Lesson
    form_class = LessonForm
    template_name = "app_web/lesson_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_initial(self):
        initial = super().get_initial()
        course_id = self.request.GET.get("course")
        if course_id:
            course = Course.objects.filter(pk=course_id, owner=self.request.user).first()
            if course:
                initial["course"] = course
        return initial

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, "Урок создан.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("app_web:course-detail", kwargs={"pk": self.object.course_id})


class LessonUpdateView(LoginRequiredMixin, OwnerOrModeratorRequiredMixin, UpdateView):
    model = Lesson
    form_class = LessonForm
    template_name = "app_web/lesson_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "Урок обновлён.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("app_web:course-detail", kwargs={"pk": self.object.course_id})


class LessonDeleteView(LoginRequiredMixin, OwnerOnlyRequiredMixin, DeleteView):
    model = Lesson
    template_name = "app_web/confirm_delete.html"

    def form_valid(self, form):
        messages.success(self.request, f"Урок «{self.object.name}» удалён.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("app_web:course-detail", kwargs={"pk": self.object.course_id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["object_type"] = "урок"
        context["cancel_url"] = reverse("app_web:course-detail", kwargs={"pk": self.object.course_id})
        return context
