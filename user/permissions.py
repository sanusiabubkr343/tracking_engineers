from rest_framework import permissions

ADMIN_ROLE = "Admin"
PROJECT_MANAGER_ROLE = "ProjectManager"
ENGINEER_ROLE = "Engineer"


class IsAdmin(permissions.BasePermission):
    """Allows access only to admin users."""

    message = "Only Admins are authorized to perform this action."

    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and request.user.role == ADMIN_ROLE)


class IsEngineer(permissions.BasePermission):
    """Allows access only to engineers."""

    message = "Only Engineers are authorized to perform this action."

    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and request.user.role == ENGINEER_ROLE)


class IsProjectManager(permissions.BasePermission):
    """Allows access only to project managers."""

    message = "Only Project Managers are authorized to perform this action."

    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and request.user.role == PROJECT_MANAGER_ROLE)
