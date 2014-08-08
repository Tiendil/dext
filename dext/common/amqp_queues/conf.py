# coding: utf-8

from django.conf import settings as project_settings

from dext.common.utils.app_settings import app_settings

amqp_settings = app_settings('AMQP',
                              ENVIRONMENT_MODULE='%s.amqp_environment' % project_settings.PROJECT_MODULE,
                              WORKERS_MANAGER_PID='dext_ampq_workers_manager')
