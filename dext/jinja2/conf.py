# coding: utf-8

from django.conf import settings as project_settings

from django_next.utils.app_settings import app_settings

settings = app_settings('DJEXT_JINJA2', 
                        TEMPLATE_DIRS=project_settings.TEMPLATE_DIRS
                        )

