from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """Faqat ADMIN roli yoki superuser kira oladi."""
    message = 'Bu amal faqat administrator uchun.'

    def has_permission(self, request, view):
        u = request.user
        return bool(
            u and u.is_authenticated and (u.is_superuser or getattr(u, 'role', None) == 'ADMIN')
        )
