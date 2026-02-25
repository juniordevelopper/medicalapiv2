from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Doctor, Reception


# ----------------------------
# CustomUser
# ----------------------------
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'status', 'is_blocked', 'is_deleted')
    list_filter = ('status', 'is_blocked', 'is_deleted')
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal info', {'fields': ('fullname', 'phone', 'profile', 'bio')}),
        ('Permissions', {'fields': ('status', 'is_blocked', 'is_deleted', 'is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined', 'last_email_sent')}),
    )
    readonly_fields = ('last_login', 'date_joined')
    search_fields = ('email', 'username', 'fullname')
    ordering = ('email',)


# ----------------------------
# Doctor
# ----------------------------
@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('user', 'hospital', 'department', 'tajriba')
    list_filter = ('hospital', 'department')
    search_fields = ('user__email', 'user__fullname')


# ----------------------------
# Reception
# ----------------------------
@admin.register(Reception)
class ReceptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'hospital')
    list_filter = ('hospital',)
    search_fields = ('user__email', 'user__fullname')
