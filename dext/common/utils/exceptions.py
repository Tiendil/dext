# coding: utf-8

from . import relations


class DextError(Exception):
    MSG = None

    def __init__(self, **kwargs):
        super(DextError, self).__init__(self.MSG % kwargs)
        self.arguments = kwargs


class ViewError(DextError):
    MSG = 'error [%(code)s] in view: %(message)s'

    @property
    def code(self): return self.arguments['code']

    @property
    def http_status(self): return self.arguments.get('http_status', relations.HTTP_STATUS.OK)

    @property
    def message(self): return self.arguments['message']

    @property
    def info(self): return self.arguments.get('info', {})


class InternalViewError(DextError):
    pass


class DuplicateViewNameError(InternalViewError):
    MSG = 'duplicate view name "%(name)s"'

class SingleNameMustBeSpecifiedError(InternalViewError):
    MSG = 'single argument name must be specified (not less, not more)'

class WrongProcessorArgumentError(InternalViewError):
    MSG = 'processor "%(processor)s" received wrong argument name "%(argument)s"'
