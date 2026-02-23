from django.contrib import admin
from .models import Chat, Message

# ----------------------------
# Chat
# ----------------------------
@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'user', 'status', 'created_at')
    ordering = ('-created_at',)

# ----------------------------
# Message
# ----------------------------
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('chat', 'sender', 'receiver', 'created_at')
    ordering = ('-created_at',)