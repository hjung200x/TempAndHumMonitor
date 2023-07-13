from django.contrib import admin
from status.models import Status

@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'value')
