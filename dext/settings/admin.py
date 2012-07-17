# -*- coding: utf-8 -*-

from django.contrib import admin

from dext.settings.models import Setting

class SettingAdmin(admin.ModelAdmin):
    list_display = ('key', 'value')

admin.site.register(Setting, SettingAdmin)
