# coding: utf-8
import subprocess

from django.conf import settings as project_settings


def normalize_email(email):
    return email.lower()


def run_django_command(command):
    return subprocess.call(['django-admin.py']+command+['--settings', '%s.settings' % project_settings.PROJECT_MODULE])


def get_ip_from_request(request):
    """Returns the IP of the request, accounting for the possibility of being
       behind a proxy.
    """
    ip = request.META.get("HTTP_X_FORWARDED_FOR", None)
    if ip:
       # X_FORWARDED_FOR returns client1, proxy1, proxy2,...
       ip = ip.split(", ")[0]
    else:
       ip = request.META.get("REMOTE_ADDR", "")
    return ip
