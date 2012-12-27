# -*- coding: utf-8 -*-
import inspect
import functools

from django.http import Http404, HttpResponse, HttpResponseNotFound, HttpResponseRedirect, HttpResponsePermanentRedirect
from django.middleware import csrf

from dext.utils import s11n, memoize
from dext.jinja2 import render

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

def validator(code=None, message=None, response_type=None):

    @functools.wraps(validator)
    def validator_decorator(checker):

        @functools.wraps(checker)
        def validator_wrapper(code=code, message=message, response_type=response_type):

            @functools.wraps(validator_wrapper)
            def view_decorator(view):

                @functools.wraps(view)
                def view_wrapper(self, *args, **kwargs):

                    if not checker(self, *args, **kwargs):
                        return self.auto_error(code=code, message=message,  response_type=response_type)

                    return view(self, *args, **kwargs)

                return view_wrapper

            return view_decorator

        return validator_wrapper

    return validator_decorator


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

@functools.total_ordering
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

    def __eq__(self, other):
        return self.path == other.path

    def __lt__(self, other):
        # print self.path, '|', other.path
        for l, r in zip(self.path, other.path):
            if not l: return True
            if not r: return False
            if l[0] == r[0] == '#': return l < r
            if l[0] == '#': return False
            if r[0] == '#': return True
            if l[0] != '#' and l != r: return l < r

        return len(self.path) < len(other.path)

class BaseResource(object):

    ERROR_TEMPLATE = None

    def __init__(self, request):
        self.request = request
        self.csrf = csrf.get_token(request)

    def initialize(self, *args, **kwargs):
        pass

    @classmethod
    @memoize.memclass
    def get_handlers(cls):

        handlers = {}

        for method_name in dir(cls):
            method = getattr(cls, method_name)

            if hasattr(method, '_handler_info'):
                info = HandlerInfo(method)
                if info.path in handlers:
                    handlers[info.path].update(info)
                else:
                    handlers[info.path] = info

        return sorted(handlers.values())

    def string(self, string):
        return HttpResponse(string, mimetype='text/html; charset=utf-8')

    def atom(self, string):
        return HttpResponse(string, mimetype='application/atom+xml; charset=utf-8')

    def rss(self, string):
        return HttpResponse(string, mimetype='application/rss+xml; charset=utf-8')

    def rdf(self, string):
        return HttpResponse(string, mimetype='application/rdf+xml; charset=utf-8')

    def template(self, template_name, context={}, mimetype='text/html; charset=utf-8', status_code=200):
        full_context = {'resource': self}
        full_context.update(context)

        response_class = HttpResponse

        if status_code == 404:
            response_class = HttpResponseNotFound

        if 'charser' not in mimetype:
            mimetype += '; charset=utf-8'

        return response_class(render.template(template_name, full_context, self.request), mimetype=mimetype)


    def json(self, **kwargs):
        response = HttpResponse(s11n.to_json(kwargs), mimetype='application/json; charset=utf-8')
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

    def auto_error(self, code, message, template=None, status_code=200, response_type=None):
        if self.request.method == 'GET' and response_type in (None, 'html') and not self.request.is_ajax():
            if template is None:
                template = self.ERROR_TEMPLATE
            return self.template(template, {'msg': message, 'error_code': code }, status_code=status_code)
        else:
            return self.json_error(code, message)

    def css(self, text):
        response = HttpResponse(text, mimetype='text/css; charset=utf-8')
        return response

    def redirect(self, url, permanent=False):
        try:
            if permanent:
                return HttpResponsePermanentRedirect(url)
            return HttpResponseRedirect(url)
        except:
            return HttpResponseRedirect('/')
