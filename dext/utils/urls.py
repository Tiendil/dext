# coding: utf8
import copy

class UrlBuilder(object):

    def __init__(self, base, arguments={}):
        self.base = base
        self.default_arguments = arguments

    def __call__(self, **kwargs):
        if not len(self.default_arguments) and not len(kwargs):
            return self.base

        arguments = copy.copy(self.default_arguments)
        arguments.update(kwargs)

        return self.base + '?' + '&'.join('%s=%s' % (key, value) for key, value in arguments.items() if value is not None)
