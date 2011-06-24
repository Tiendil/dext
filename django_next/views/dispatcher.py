# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url

from .resources import ResourceException

def create_handler_view(resource_class, handler):

    def handler_view(request, *args, **kwargs):
        resource = resource_class(request, *args, **kwargs)
        method_name = handler.dispatch(request)
        method = getattr(resource, method_name, None)
        if method:
            return method()
        raise ResourceException('can not dispatch url for handler "%s"' % handler.path[-1])

    handler_view.__name__ = '%s_%s' % (resource_class.__name__, handler.path[-1])

    return handler_view


def resource_patterns(resource_class):
    patterns_args = ['']

    for handler in resource_class.get_handlers():
        patterns_args.append( url(handler.url_regexp, 
                                  create_handler_view(resource_class, handler),
                                  name=handler.path[-1]) )

    return patterns(*patterns_args)
