# coding: utf-8

from django import apps as django_apps

class Config(django_apps.AppConfig):
    name = 'dext.common.utils'
    label = 'dext_utils'
    verbose_name = 'Dext utils'
