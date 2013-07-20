# coding: utf-8
import inspect
import functools

from django.http import Http404, HttpResponse, HttpResponseNotFound, HttpResponseRedirect, HttpResponsePermanentRedirect
from django.middleware import csrf

from dext.utils import s11n, memoize
from dext.utils.response import mime_type_to_response_type
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
    DIALOG_ERROR_TEMPLATE = None

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

    @property
    def user_ip(self):
        """Returns the IP of the request, accounting for the possibility of being
        behind a proxy.
        """
        ip = self.request.META.get("HTTP_X_FORWARDED_FOR", None)
        if ip:
            # X_FORWARDED_FOR returns client1, proxy1, proxy2,...
            ip = ip.split(", ")[0]
        else:
            ip = self.request.META.get("REMOTE_ADDR", "")
        return ip

    def string(self, string, charset='utf-8'):
        return HttpResponse(string, mimetype='text/html; charset=%s' % charset)

    def xml(self, string, charset='utf-8'):
        return HttpResponse(string, mimetype='text/xml; charset=%s' % charset)

    def atom(self, string, charset='utf-8'):
        return HttpResponse(string, mimetype='application/atom+xml; charset=%s' % charset)

    def rss(self, string, charset='utf-8'):
        return HttpResponse(string, mimetype='application/rss+xml; charset=%s' % charset)

    def rdf(self, string, charset='utf-8'):
        return HttpResponse(string, mimetype='application/rdf+xml; charset=%s' % charset)

    def template(self, template_name, context={}, status_code=200, charset='utf-8'):
        full_context = {'resource': self}
        full_context.update(context)

        response_class = HttpResponse

        if status_code == 404:
            response_class = HttpResponseNotFound

        return response_class(render.template(template_name, full_context, self.request), mimetype='text/html; charset=%s' % charset)


    def json(self, charset='utf-8', **kwargs):
        response = HttpResponse(s11n.to_json(kwargs), mimetype='application/json; charset=%s' % charset)
        return response

    def json_ok(self, data=None, charset='utf-8'):
        if data is None:
            return self.json(status='ok', charset=charset)
        return self.json(status='ok', data=data, charset=charset)

    def json_processing(self, status_url, charset='utf-8'):
        return self.json(status='processing', status_url=status_url, charset=charset)

    def json_error(self, code, messages=None, charset='utf-8'):
        data = {'status': 'error',
                'code': code,
                'charset': charset}
        if isinstance(messages, basestring):
            data['error'] = messages
        else:
            data['errors'] = messages

        return self.json(**data)

    def auto_error(self, code, message, template=None, status_code=200, response_type=None, charset='utf-8'):

        if response_type is None:
            response_type = mime_type_to_response_type(self.request.META.get('HTTP_ACCEPT'))

        if response_type == 'html':
            if self.request.is_ajax():
                return self.template(self.DIALOG_ERROR_TEMPLATE, {'msg': message, 'error_code': code }, status_code=status_code)
            else:
                return self.template(self.ERROR_TEMPLATE, {'msg': message, 'error_code': code }, status_code=status_code)

        return self.json_error(code, message, charset=charset)

    def css(self, text, charset='utf-8'):
        response = HttpResponse(text, mimetype='text/css; charset=%s' % charset)
        return response

    def redirect(self, url, permanent=False):
        try:
            if permanent:
                return HttpResponsePermanentRedirect(url)
            return HttpResponseRedirect(url)
        except:
            return HttpResponseRedirect('/')
