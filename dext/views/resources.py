# -*- coding: utf-8 -*-
import inspect
import functools

from django.http import Http404, HttpResponse, HttpResponseNotFound
from django.middleware import csrf
from django.shortcuts import redirect

from ..utils import s11n
from ..jinja2 import render

class ResourceException(Exception): pass

def handler(*path, **params):

    method = params.get('method', ['post', 'get'])
    args = params.get('args', [])
    name = params.get('name', path[-1])

    @functools.wraps(handler)
    def decorator(func):

        if hasattr(method, '__iter__'):
            methods = list(method)
        else:
            methods = [method]

        expected_args, expected_vargs, expected_kwargs, expected_defaults = inspect.getargspec(func)

        if expected_defaults is not None:
            expected_defaults = dict(zip(expected_args[-len(expected_defaults):], expected_defaults))

        info = {'methods': methods,
                'args': args,
                'path': path,
                'name': name,
                'expected': { 'args': expected_args,
                              'defaults': expected_defaults} }

        func._handler_info = info
        return func

    return decorator

class DispatchInfo(object):

    def __init__(self, handler_name, methods, args=[]):
        self.handler_name = handler_name
        self.methods = methods
        self.args = args

    def check(self, request):
        if request.method.lower() not in self.methods:
            return False

        for arg in self.args:

            if isinstance(arg, basestring) or not hasattr(arg, '__iter__'):
                key = arg
                if arg not in request.GET: return False

            elif len(arg) == 2:
                key, value = arg
                if key not in request.GET: return False
                if value != request.GET[key]: return False

        return True


class HandlerInfo(object):

    def __init__(self, method):
        info = method._handler_info

        dispatch_info = DispatchInfo(handler_name=method.__name__,
                                     methods=info['methods'],
                                     args=info['args'])

        self.dispatch_list = [dispatch_info]

        self.path = info['path']
        self.name = info['name']


    def update(self, handler_info):
        if self.path != handler_info.path:
            raise ResourceException('can not merge handlers with different path: ("%s", "%s")' % (self.path, handler_info.path) )

        self.dispatch_list.extend(handler_info.dispatch_list)
        self.dispatch_list.sort(key=lambda x: x.handler_name)

    @property
    def url_regexp(self):
        regex = ''
        for part in self.path:
            if len(part) == 0:
                regex = '%s/' % regex
            elif part[0] == '#':
                regex = '%s/(?P<%s>[^\/]*)' % (regex, part[1:])
            elif part[0] == '^':
                regex = '%s/%s' % (regex, part[1:])
            else:
                regex = '%s/%s' % (regex, part)
        return '^%s$' % regex[1:]

    def dispatch(self, request):
        for dispatch_info in self.dispatch_list:
            if dispatch_info.check(request):
                return dispatch_info.handler_name
        raise Http404()



class BaseResource(object):

    def __init__(self, request, *args, **kwargs):
        self.request = request
        self.csrf = csrf.get_token(request)

    @classmethod
    def get_handlers(cls):

        if hasattr(cls, '_handlers'):
            return cls._handlers

        handlers = {}

        for method_name in dir(cls):
            method = getattr(cls, method_name)

            if hasattr(method, '_handler_info'):
                info = HandlerInfo(method)
                if info.path in handlers:
                    handlers[info.path].update(info)
                else:
                    handlers[info.path] = info

        cls._handlers = handlers.values()
        return cls._handlers

    def string(self, string):
        return HttpResponse(string, mimetype='text/html')

    def atom(self, string):
        return HttpResponse(string, mimetype='application/atom+xml')

    def rss(self, string):
        return HttpResponse(string, mimetype='application/rss+xml')

    def rdf(self, string):
        return HttpResponse(string, mimetype='application/rdf+xml')

    def template(self, template_name, context={}, mimetype='text/html', status_code=200):
        full_context = {'resource': self}
        full_context.update(context)

        response_class = HttpResponse

        if status_code == 404:
            response_class = HttpResponseNotFound

        return response_class(render.template(template_name, full_context, self.request), mimetype=mimetype)


    def json(self, **kwargs):
        response = HttpResponse(s11n.to_json(kwargs), mimetype='application/json')
        return response

    def json_ok(self, data=None):
        if data is None:
            return self.json(status='ok')
        return self.json(status='ok', data=data)

    def json_processing(self, status_url):
        return self.json(status='processing', status_url=status_url)

    def json_error(self, code, messages=None):
        data = {'status': 'error',
                'code': code}
        if isinstance(messages, basestring):
            data['error'] = messages
        else:
            data['errors'] = messages

        return self.json(**data)

    def css(self, text):
        response = HttpResponse(text, mimetype='text/css')
        return response

    def redirect(self, url, permanent=False):
        response = redirect(url, permanent=permanent)
        return response
