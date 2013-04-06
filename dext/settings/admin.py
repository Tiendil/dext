# coding: utf-8

from django.contrib import admin

from dext.settings.models import Setting

class SettingAdmin(admin.ModelAdmin):
    list_display = ('key', 'value', 'updated_at')

    def save_model(self, request, obj, form, change):
        from dext.settings import settings
        settings[obj.key] = obj.value

    def delete_model(self, request, obj):
        from dext.settings import settings
        del settings[obj.key]

admin.site.register(Setting, SettingAdmin)
