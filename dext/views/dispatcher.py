# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

from .resources import ResourceException

def create_handler_view(resource_class, handler):

    if isinstance(handler, basestring): 
        handler_path = '%s::%s' % (resource_class.__name__, handler)
        result_method_name = handler # TODO: result_method_name - is some fucking variable name, since 'handler_name' not seen in handler_view 
    else:
        handler_path = handler.path[-1]
        result_method_name = None


    def handler_view(request, *args, **kwargs):     

        resource = resource_class(request, *args, **kwargs)
        if result_method_name is None:
            method_name = handler.dispatch(request)
        else:
            method_name = result_method_name
        method = getattr(resource, method_name, None)

        info = method._handler_info

        args = info['expected']['args']
        defaults = info['expected']['defaults']

        arguments = {}
        for arg in args:
            if arg != 'self':
                if arg in request.GET:
                    arguments[arg] = request.GET.get(arg)
                elif defaults and arg not in defaults:
                    raise ResourceException('can not dispatch url for handler "%s:%s" - value for argument "%s" in view "%s" does not defined' % 
                                            (resource.__class__.__name__, handler_path, arg, method))

        if method:
            return method(**arguments)

        raise ResourceException('can not dispatch url for handler "%s"' % handler_path)

    handler_view.__name__ = '%s_%s' % (resource_class.__name__, handler_path)

    return handler_view


def resource_patterns(resource_class):
    patterns_args = ['']

    for handler in resource_class.get_handlers():
        patterns_args.append( url(handler.url_regexp, 
                                  create_handler_view(resource_class, handler),
                                  name=handler.name) )

    return patterns(*patterns_args)
