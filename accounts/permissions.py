from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.status == 4)

class IsDirector(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.status == 3)

class IsDoctor(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.status == 2)

class IsReception(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.status == 1)

class IsPatient(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.status == 0)


class IsDirector(permissions.BasePermission):
    """
    Faqat directorlar uchun ruxsat
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_director)

class IsDirectorOfHospital(permissions.BasePermission):
    """
    Director faqat o'z shifoxonasi uchun ruxsat
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated or not request.user.is_director:
            return False
        
        # Director o'z shifoxonasiga ega
        return hasattr(request.user, 'managed_hospital')

    def has_object_permission(self, request, view, obj):
        # Ob'ektni tekshirish (Doctor, Reception yoki Queue)
        if hasattr(obj, 'hospital'):
            return obj.hospital == request.user.managed_hospital
        elif hasattr(obj, 'doctor') and hasattr(obj.doctor, 'hospital'):
            return obj.doctor.hospital == request.user.managed_hospital
        return False