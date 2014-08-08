# coding: utf-8

from django.utils.importlib import import_module

from dext.common.amqp_queues.conf import amqp_settings
from dext.common.amqp_queues.workers import BaseWorker


class Workers(object):

    def __init__(self):
        pass

    def __iter__(self):
        return (worker
                for worker in self.__dict__.values()
                if isinstance(worker, BaseWorker) )

    def get_by_name(self, name):
        for worker in self.__dict__.values():
            if isinstance(worker, BaseWorker) and worker.name == name:
                    return worker
        return None



class BaseEnvironment(object):

    def __init__(self):
        self.initialized = False
        self.initializing = False
        self._workers = Workers()

    @property
    def workers(self):

        if not self.initialized and not self.initializing:
            self.initializing = True
            self.initialize()
            self.initializing = False

        return self._workers

    def initialize(self):
        self.initialized = True

    def deinitialize(self):
        self.initialized = False


def get_environment():
    module = import_module(amqp_settings.ENVIRONMENT_MODULE)
    return module.environment
