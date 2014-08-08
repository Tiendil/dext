# coding: utf-8

import subprocess

from django.core.management.base import BaseCommand
from django.conf import settings as project_settings

from dext.common.utils import discovering
from dext.common.utils.logic import run_django_command


class Command(BaseCommand):

    help = 'run tests for all non-django applications'

    requires_model_validation = False

    def handle(self, *args, **options):
        subprocess.call("rm -f `find ./ -name '*.pyc'`", shell=True)

        tests = []
        for app_label in project_settings.INSTALLED_APPS:
            label = app_label.split('.')

            if label[0] == 'django':
                continue

            tests_path = '%s.tests' % app_label
            if discovering.is_module_exists(tests_path):
                tests.append(tests_path)

        run_django_command(['test'] + tests)
