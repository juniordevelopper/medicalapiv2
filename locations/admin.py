
from django.contrib import admin
from .models import Location

# ----------------------------
# Location
# ----------------------------
@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name',)
    ordering = ('name',)
