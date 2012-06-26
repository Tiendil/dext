#coding: utf-8
from django.http import HttpResponse

from . import s11n

class Http403(Exception):

    def __init__(self, msg=u'У вас нет прав для проведения операции'):
        self.msg = msg

class Error(Exception):

    def __init__(self, msg):
        self.msg = msg

class ExceptionMiddleware(object):
    '''
    abstract class, MUST be inherited (EXCEPTION_VIEW must be defined)
    '''

    EXCEPTION_RESOURCE = None

    def process_exception(self, request, exception):

        if isinstance(exception, Http403):
            if request.is_ajax() or request.method.lower() == 'post':
                return HttpResponse(s11n.to_json({'status': 'error',
                                                  'code': 403,
                                                  'error': exception.msg}),
                                    mimetype='application/json')
            return self.EXCEPTION_RESOURCE(request).handler403(msg=exception.msg)

        if isinstance(exception, Error):
            if request.is_ajax() or request.method.lower() == 'post':
                return HttpResponse(s11n.to_json({'status': 'error',
                                                  'error': exception.msg}),
                                    mimetype='application/json')
            return self.EXCEPTION_RESOURCE(request).error(msg=exception.msg)
