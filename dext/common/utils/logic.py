# coding: utf-8
import subprocess

from django.conf import settings as project_settings


def normalize_email(email):
    dog_index = email.rfind('@')
    return email[:dog_index] + email[dog_index:].lower()


def run_django_command(command):
    return subprocess.call(['django-admin.py']+command+['--settings', '%s.settings' % project_settings.PROJECT_MODULE])
