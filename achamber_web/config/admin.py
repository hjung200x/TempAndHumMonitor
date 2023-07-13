from django.contrib import admin
from config.models import ConfigTbl

@admin.register(ConfigTbl)
class ConfigTblAdmin(admin.ModelAdmin):
    list_display = ('key', 'value')
