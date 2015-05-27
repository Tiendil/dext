# coding: utf-8

from django import apps as django_apps

class Config(django_apps.AppConfig):
    name = 'dext.common.meta_relations'
    label = 'dext_meta_relations'
    verbose_name = 'Dext meta relations'

    def ready(self):
        from . import logic
        logic.autodiscover_relations()
        logic.autodiscover_types()
