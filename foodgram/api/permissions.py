from rest_framework import permissions


class OwnerOrReadOnly(permissions.BasePermission):
    """Разрешение на изменение/удаление собственного контента."""

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (request.user == obj.author and request.method != "PUT"
                or request.method in permissions.SAFE_METHODS)


class ReadOnly(permissions.BasePermission):
    """Разрешение только для чтения."""
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        return request.method in permissions.SAFE_METHODS
