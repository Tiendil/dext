# coding: utf-8

import functools

from django.conf.urls import patterns, url
from django.http import HttpResponse, HttpResponseRedirect, HttpResponsePermanentRedirect

from dext.common.utils import exceptions
from dext.common.utils import relations
from dext.common.utils import s11n
from dext.common.utils.conf import utils_settings

slots = lambda *argv: tuple(argv)

class Context(object):

    def __setattr__(self, name, value):
        if hasattr(self, name):
            raise exceptions.ViewError(code='internal.try_to_reassign_context_value',
                                       message=utils_settings.DEFAUL_ERROR_MESSAGE)
        super(Context, self).__setattr__(name, value)


class View(object):

    def __init__(self, logic):
        self.processors = []
        self.logic = logic
        self.name = None
        self.path = None
        self.resource = None

    def get_processors(self):
        return self.resource.get_processors() + self.processors

    def add_processor(self, processor):
        self.processors.insert(0, processor)

    def __call__(self, request, **url_arguments):
        context = Context()

        context.django_request = request
        context.django_url_argumens = url_arguments

        context.dext_view = self
        context.dext_error_prefix = '%s.%s' % (self.resource.name, self.name)

        unprocessed_processors = self.get_processors()

        processed_processors = []

        response = None

        try:
            for processor in unprocessed_processors:
                response = processor.preprocess(context)
                processed_processors.append(processor)

                if response:
                    break

            if response is None:
                response = self.logic(context)

            for processor in reversed(processed_processors):
                response = processor.postprocess(context, response)

                if response:
                    break

            return response.complete(context)

        except exceptions.ViewError as error:
            return self.process_error(error, request, context)


    def _get_error_response_class(self, request):

        accepted_mimetypes = request.META.get('HTTP_ACCEPT')

        if accepted_mimetypes is None:
            return AjaxError

        if any(tp in accepted_mimetypes for tp in ('application/xhtml+xml', 'text/html', 'text/plain', 'text/xml')):
            return PageError

        if any(tp in accepted_mimetypes for tp in ('application/x-javascript',)):
            return NotImplemented

        return AjaxError


    def process_error(self, error, request, context):
        error_response_class = self._get_error_response_class(request)
        return error_response_class(code=error.code, errors=error.message, context=context).complete(context)


    def get_url_record(self):

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

        return url('^%s$' % regex[1:],
                   self,
                   name=self.name,
                   kwargs={})


    def __lt__(self, other):
        for l, r in zip(self.path, other.path):
            if not l: return True
            if not r: return False
            if l[0] == r[0] == '#': return l < r
            if l[0] == '#': return False
            if r[0] == '#': return True
            if l[0] != '#' and l != r: return l < r

        return len(self.path) < len(other.path)




class Resource(object):
    __slots__ = ('name', 'processors', 'views', 'parent', 'children')

    def __init__(self, name):
        super(Resource, self).__init__()
        self.name = name
        self.processors = []
        self.views = {}
        self.parent = None
        self.children = []

    def get_processors(self):
        if self.parent:
            return self.parent.get_processors() + self.processors

        return self.processors

    def add_processor(self, processor):
        self.processors.append(processor)

    def add_child(self, child):
        self.children.append(child)
        child.parent = self

    def handler(self, *argv, **kwargs):

        name = kwargs.get('name', argv[-1])

        methods = kwargs.get('method', ('get',))

        if isinstance(methods, basestring):
            methods = [methods]

        methods = [m.upper() for m in methods]

        @functools.wraps(self.handler)
        def decorator(func):

            view = func if isinstance(func, View) else View(logic=func)

            # view = functools.wraps(view.logic)(view)

            view.name = name
            view.path = argv

            view.add_processor(HttpMethodProcessor(allowed_methods=methods))

            if view.name in self.views:
                raise exceptions.DuplicateViewNameError(name=view.name)

            self.views[view.name] = view
            view.resource = self

            return view

        return decorator


    def get_urls(self):
        urls = []

        for view in sorted(self.views.values()):
            urls.append(view.get_url_record())

        return patterns('', *urls)


class BaseViewProcessor(object):
    __slots__ = ()

    def __init__(self): pass

    def preprocess(self, context):
        pass

    def postprocess(self, context, response):
        return response

    @classmethod
    def handler(cls, *argv, **kwargs):

        @functools.wraps(cls.handler)
        def decorator(func):

            view = func if isinstance(func, View) else View(logic=func)

            handler = cls(*argv, **kwargs)

            view.add_processor(handler)

            return view

        return decorator



class HttpMethodProcessor(BaseViewProcessor):
    __slots__ = slots('allowed_methods', *BaseViewProcessor.__slots__)

    def __init__(self, allowed_methods):
        super(HttpMethodProcessor, self).__init__()
        self.allowed_methods = frozenset(allowed_methods)

    def preprocess(self, context):
        if context.django_request.method not in self.allowed_methods:
            raise exceptions.ViewError(code=u'common.wrong_http_method',
                                       message=u'К адресу нельзя обратиться с помощью HTTP метода "%(method)s"' % context.django_request.method)

        context.django_method = relations.HTTP_METHOD.index_name[context.django_request.method]


class PermissionProcessor(BaseViewProcessor):
    __slots__ = slots('permission', 'context_name', *BaseViewProcessor.__slots__)

    def __init__(self, permission, context_name):
        super(PermissionProcessor, self).__init__()
        self.permission = permission
        self.context_name = context_name

    def preprocess(self, context):
        setattr(context, self.context_name, context.django_request.user.has_perm(self.permission))


class AccessProcessor(BaseViewProcessor):
    __slots__ = BaseViewProcessor.__slots__

    ERROR_CODE = NotImplemented
    ERROR_MESSAGE = NotImplemented

    def check(self, context):
        raise NotImplementedError()

    def preprocess(self, context):
        if not self.check(context):
            raise exceptions.ViewError(code=self.ERROR_CODE, message=self.ERROR_MESSAGE)


class FormProcessor(BaseViewProcessor):
    __slots__ = slots('error_message', 'form_class', 'context_name', *BaseViewProcessor.__slots__)

    def __init__(self, form_class, context_name='form', **kwargs):
        super(FormProcessor, self).__init__(**kwargs)
        self.form_class = form_class
        self.context_name = context_name

    def preprocess(self, context):

        form = self.form_class(context.django_request.POST)

        if not form.is_valid():
            raise exceptions.ViewError(code='%s.form_errors' % context.dext_error_prefix, message=form.errors)

        setattr(context, self.context_name, form)



class ArgumentProcessor(BaseViewProcessor):
    __slots__ = slots('error_message', 'get_name', 'post_name', 'url_name', 'context_name', 'default_value', *BaseViewProcessor.__slots__)

    def __init__(self, context_name, error_message=None, get_name=None, post_name=None, url_name=None, default_value=NotImplemented):
        super(ArgumentProcessor, self).__init__()

        if sum((1 if get_name else 0,
                1 if post_name else 0,
                1 if url_name else 0)) != 1:
            raise exceptions.SingleNameMustBeSpecifiedError()

        self.error_message = error_message
        self.url_name = url_name
        self.get_name = get_name
        self.post_name = post_name
        self.context_name = context_name
        self.default_value = default_value

    def extract(self, context):
        if self.url_name:
            return context.django_url_argumens.get(self.url_name)

        if self.get_name:
            return context.django_request.GET.get(self.get_name)

        return context.django_request.POST.get(self.post_name)

    def parse(self, context, raw_value):
        raise NotImplementedError()

    def _argument_name(self):
        if self.url_name:
            return self.url_name
        if self.get_name:
            return self.get_name
        if self.post_name:
            return self.post_name

    def raise_not_specified(self, context):
        raise exceptions.ViewError(code='%s.%s.not_specified' % (context.dext_error_prefix, self._argument_name()), message=self.error_message)

    def raise_wrong_format(self, context):
        raise exceptions.ViewError(code='%s.%s.wrong_format' % (context.dext_error_prefix, self._argument_name()), message=self.error_message)

    def raise_wrong_value(self, context):
        raise exceptions.ViewError(code='%s.%s.wrong_value' % (context.dext_error_prefix, self._argument_name()), message=self.error_message)

    def preprocess(self, context):

        raw_value = self.extract(context)

        if raw_value:
            value = self.parse(context, raw_value)

        elif self.default_value is NotImplemented:
            self.raise_not_specified(context=context)

        else:
            value = self.default_value

        setattr(context, self.context_name, value)



class RelationArgumentProcessor(ArgumentProcessor):
    __slots__ = slots('relation', 'value_type', *ArgumentProcessor.__slots__)

    def __init__(self, relation, value_type=int, **kwargs):
        super(RelationArgumentProcessor, self).__init__(**kwargs)
        self.relation = relation
        self.value_type = value_type

    def parse(self, context, raw_value):
        from rels import exceptions as rels_exceptions

        try:
            value = self.value_type(raw_value)
        except TypeError:
            self.raise_wrong_format()

        try:
            return self.relation(value)
        except rels_exceptions.NotExternalValueError:
            self.raise_wrong_value()




class BaseResponse(object):
    __slots__ = ('http_status',
                 'http_mimetype',
                 'http_charset',
                 'content')

    def __init__(self,
                 http_mimetype,
                 http_status = relations.HTTP_STATUS.OK,
                 http_charset='utf-8',
                 content={}):
        self.http_status = http_status
        self.http_mimetype = http_mimetype
        self.http_charset = http_charset
        self.content = content

    def complete(self, context):
        return HttpResponse(self.content,
                            status=self.http_status.value,
                            mimetype='%s; charset=%s' % (self.http_mimetype, self.http_charset))


class Redirect(BaseResponse):
    __slots__ = slots('target_url', 'permanent', *BaseResponse.__slots__)

    def __init__(self, target_url, permanent=False, **kwargs):
        super(Redirect, self).__init__(http_mimetype=None, **kwargs)
        self.target_url = target_url
        self.permanent = permanent

    def complete(self, context):
        ResponseClass = HttpResponsePermanentRedirect if self.permanent else HttpResponseRedirect
        return ResponseClass(self.target_url)


class Page(BaseResponse):
    __slots__ = slots('template', *BaseResponse.__slots__)

    def __init__(self, template, http_mimetype='text/html', **kwargs):
        super(Page, self).__init__(http_mimetype=http_mimetype, **kwargs)
        self.template = template

    def complete(self, context):
        from dext.jinja2 import render
        self.content = render.template(self.template, self.content, context.django_request)
        return super(Page, self).complete(context)


# TODO: refactor error/errors
class PageError(Page):
    __slots__ = slots('code', 'errors', 'context', *Page.__slots__)

    def __init__(self, code, errors, context, **kwargs):
        if 'template' not in kwargs:
            # TODO: errors for dialogs
            kwargs['template'] = utils_settings.PAGE_ERROR_TEMPLATE

        if isinstance(errors, basestring):
            error = errors
        else:
            error = errors[0]

        if 'content' not in kwargs:
            kwargs['content'] = {}

        kwargs['content'].update({'error_code': code,
                                  'error_message': error,
                                  'context': context,
                                  'resource': context.resource})# TODO: remove resource (added for compartibility with old version)

        super(PageError, self).__init__(**kwargs)

        self.code = code
        self.errors = error
        self.context = context



class Ajax(BaseResponse):
    __slots__ = BaseResponse.__slots__

    def __init__(self, http_mimetype='application/json', **kwargs):
        super(Ajax, self).__init__(http_mimetype=http_mimetype, **kwargs)

    def wrap(self, context):
        return context

    def complete(self, context):
        self.content = s11n.to_json(self.wrap(self.content))
        return super(Ajax, self).complete(context)


class AjaxOk(Ajax):
    def wrap(self, context):
        return {'status': 'ok', 'data': context}


# TODO: refactor error/errors
class AjaxError(Ajax):
    __slots__ = slots('code', 'errors', 'context', *BaseResponse.__slots__)

    def __init__(self, code, errors, context, **kwargs):
        super(AjaxError, self).__init__(**kwargs)
        self.code = code
        self.errors = errors
        self.context = context

    def wrap(self, context):
        data = {}

        if isinstance(self.errors, basestring):
            data['error'] = self.errors
        else:
            data['errors'] = self.errors

        return {'status': 'error',
                'code': self.code,
                'data': data}


class AjaxProcessing(Ajax):
    __slots__ = slots('status_url', *BaseResponse.__slots__)

    def __init__(self, status_url, **kwargs):
        super(AjaxProcessing, self).__init__(**kwargs)
        self.status_url = status_url

    def wrap(self, context):
        return {'status': 'processing',
                'status_url': self.status_url}
