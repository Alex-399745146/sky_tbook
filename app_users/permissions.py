# app_users/permissions.py

from rest_framework.permissions import BasePermission

MODERATOR_GROUP = "moderators"


def is_moderator(user) -> bool:
    """Модератор — суперпользователь или участник группы ``moderators``."""
    return bool(
        user and user.is_authenticated and (user.is_superuser or user.groups.filter(name=MODERATOR_GROUP).exists())
    )


class IsModer(BasePermission):
    """Пользователь состоит в группе ``moderators`` (или суперпользователь)."""

    def has_permission(self, request, view):
        return is_moderator(request.user)


class IsNotModer(BasePermission):
    """Создавать объекты могут только обычные пользователи, не модераторы."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and not is_moderator(request.user))


class IsOwner(BasePermission):
    """Пользователь является владельцем объекта."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return getattr(obj, "owner", None) == request.user


class IsOwnerOrModerator(BasePermission):
    """Доступ к объекту имеют его владелец и модераторы."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return is_moderator(request.user) or getattr(obj, "owner", None) == request.user


class IsOwnerOnly(BasePermission):
    """Доступ только у владельца: модераторы намеренно исключены."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return not is_moderator(request.user) and getattr(obj, "owner", None) == request.user


class IsSelfOrModerator(BasePermission):
    """Пользователь может работать со своим профилем, модератор — с любым."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return is_moderator(request.user) or obj == request.user
