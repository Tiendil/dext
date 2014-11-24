# coding: utf-8

class DextError(Exception):
    MSG = None

    def __init__(self, **kwargs):
        super(DextError, self).__init__(self.MSG % kwargs)
        self.arguments = kwargs


class ViewError(DextError):
    MSG = u'error [%(code)s] in view: %(message)s'

    @property
    def code(self): return self.arguments['code']

    @property
    def message(self): return self.arguments['message']

class InternalViewError(DextError):
    pass


class DuplicateViewNameError(InternalViewError):
    MSG = u'duplicate view name "%(name)s"'

class SingleNameMustBeSpecifiedError(InternalViewError):
    MSG = u'single argument name must be specified (not less, not more)'
