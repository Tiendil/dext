# coding: utf-8
import subprocess

from django.core.management.base import BaseCommand
from django.apps import apps as django_apps

from dext.common.utils import discovering
from dext.common.utils.logic import run_django_command


class Command(BaseCommand):

    help = 'run tests for all non-django applications'

    requires_model_validation = False

    def handle(self, *args, **options):
        subprocess.call("rm -f `find ./ -name '*.pyc'`", shell=True)

        tests = []
        for application in django_apps.get_app_configs():
            label = application.name.split('.')

            if label[0] == 'django':
                continue

            tests_path = '%s.tests' % application.name
            if discovering.is_module_exists(tests_path):
                tests.append(tests_path)

        result = run_django_command(['test', '--nomigrations'] + tests)

        print('test result: ', result)
