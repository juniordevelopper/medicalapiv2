from django.contrib import admin
from .models import Queue

# ----------------------------
# Queue
# ----------------------------
@admin.register(Queue)
class QueueAdmin(admin.ModelAdmin):
    list_display = ('date', 'doctor', 'user', 'number', 'status', 'reception', 'created_at')
    ordering = ('date', 'number')