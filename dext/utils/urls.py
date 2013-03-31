# coding: utf8
import copy
from django.conf import settings as project_settings

class UrlBuilder(object):

    def __init__(self, base, protocol='http', arguments={}):
        self.base = base
        self.default_arguments = arguments
        self.protocol = protocol

    @property
    def arguments_names(self): return self.default_arguments.keys()

    def __call__(self, **kwargs):
        if not len(self.default_arguments) and not len(kwargs):
            return self.base

        arguments = copy.copy(self.default_arguments)
        arguments.update(kwargs)

        return self.protocol + '://' + project_settings.SITE_URL + self.base + '?' + '&'.join('%s=%s' % (key, value) for key, value in arguments.items() if value is not None)
