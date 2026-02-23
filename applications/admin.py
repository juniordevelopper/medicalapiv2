from django.contrib import admin
from .models import Application

# ----------------------------
# Application
# ----------------------------
@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'active', 'created_at')
    ordering = ('-created_at',)