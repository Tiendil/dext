# coding: utf8
import copy
import urllib

from django.core.urlresolvers import reverse
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

        return self.base + '?' + '&'.join('%s=%s' % (key, value) for key, value in arguments.items() if value is not None)


def url(*args, **kwargs):
    base_url = reverse(args[0], args=args[1:])
    if kwargs:
        query = urllib.urlencode(kwargs)
        base_url = '%s?%s' % (base_url, query)
    return base_url

def full_url(protocol, *args, **kwargs):
    return protocol + '://' + project_settings.SITE_URL + url(*args, **kwargs)

def absolute_url(relative_url, protocol='http'):
    return protocol + '://' + project_settings.SITE_URL + relative_url
