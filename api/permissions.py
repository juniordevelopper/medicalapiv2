from rest_framework import permissions

class IsAdminUserStatus(permissions.BasePermission):
    """
    Admin (status=3) uchun barcha huquqlar, 
    boshqalar uchun esa faqat ko'rish (GET) huquqi.
    """
    def has_permission(self, request, view):
        # 1. Agar so'rov xavfsiz bo'lsa (GET, HEAD, OPTIONS) - hamma ko'ra oladi
        if request.method in permissions.SAFE_METHODS:
            return True

        # 2. Agar so'rov tahrirlash bo'lsa (POST, PUT, DELETE) - faqat status=3 (Admin)
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.status == 4 # Sizning modelingizdagi Admin statusi
        )
