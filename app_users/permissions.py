# app_users/permissions.py

from rest_framework.permissions import BasePermission


class IsModer(BasePermission):
    """
    Пользователь состоит в группе 'moderators'.
    """

    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and user.groups.filter(name="moderators").exists()


class IsOwner(BasePermission):
    """
    Пользователь является владельцем объекта.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user
        # предполагаем, что у obj есть поле owner
        return user.is_authenticated and getattr(obj, "owner", None) == user
