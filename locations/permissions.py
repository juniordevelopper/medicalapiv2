from rest_framework import permissions

class IsAdminUserStatus(permissions.BasePermission):
    def has_permission(self, request, view):
        # Faqat tizimga kirgan va statusi 4 (Admin) bo'lganlarga ruxsat
        return bool(request.user and request.user.is_authenticated and request.user.status == 4)
