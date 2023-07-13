from django.contrib import admin
from monitor.models import Monitor

@admin.register(Monitor)
class MonitorAdmin(admin.ModelAdmin):
    list_display = ('date', 'temperature', 'hummidity')
