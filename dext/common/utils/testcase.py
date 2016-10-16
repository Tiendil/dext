# coding: utf-8
import functools
import contextlib

from io import StringIO

from django.core.handlers.wsgi import WSGIRequest
from django.test import TestCase as DjangoTestCase, TransactionTestCase as DjangoTransactionTestCase
from django.contrib.auth.models import AnonymousUser
from django.test.client import RequestFactory

from dext.common.utils import s11n

def make_request_decorator(method):

    @functools.wraps(method)
    def make_request_wrapper(self, url, meta={}, user=None, session=None):
        request = method(self, url, meta=meta)
        request.user = user if user is not None else AnonymousUser()
        request.session = session if session is not None else {}
        return request

    return make_request_wrapper


class TestCaseMixin(object):

    def fake_request(self, path='/', user=None, method='GET', csrf=None, ajax=False):
        request = WSGIRequest( { 'REQUEST_METHOD': method.upper(),
                                 'PATH_INFO': path,
                                 'wsgi.input': StringIO(),
                                 'CSRF_COOKIE': csrf,
                                 'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest' if ajax else None})
        request.user = AnonymousUser() if user is None else user
        return request

    def check_logged_in(self, account=None):
        self.assertIn('_auth_user_id', self.client.session)

        if account:
            self.assertEqual(account.id, int(self.client.session['_auth_user_id']))

    def check_logged_out(self):
        self.assertNotIn('_auth_user_id', self.client.session)

    def check_html_ok(self, response, status_code=200, texts=[], content_type='text/html', encoding='utf-8', body=None):
        self.assertEqual(response.status_code, status_code)

        self.assertTrue(content_type in response['Content-Type'])
        self.assertTrue(encoding in response['Content-Type'])

        content = response.content.decode(encoding)

        if body is not None:
            self.assertEqual(content, body)

        for text in texts:
            if isinstance(text, tuple):
                substr, number = text
                substr = str(substr)
                self.assertEqual((substr, content.count(substr)), (substr, number))
            else:
                substr = str(text)
                self.assertEqual((substr, substr in content), (substr, True))

    def check_xml_ok(self, *argv, **kwargs):
        if 'content_type' not in kwargs:
            kwargs['content_type'] = 'text/xml'
        return self.check_html_ok(*argv, **kwargs)

    def check_ajax_ok(self, response, data=None, content_type='application/json', encoding='utf-8'):
        self.assertTrue(content_type in response['Content-Type'])
        self.assertTrue(encoding in response['Content-Type'])

        self.assertEqual(response.status_code, 200)
        content = s11n.from_json(response.content.decode(encoding))

        self.assertEqual(content['status'], 'ok')

        if data is not None:
            self.assertEqual(content['data'], data)

        return content.get('data')


    def check_ajax_error(self, response, code, content_type='application/json', encoding='utf-8'):
        self.assertTrue(content_type in response['Content-Type'])
        self.assertTrue(encoding in response['Content-Type'])

        self.assertEqual(response.status_code, 200)
        data = s11n.from_json(response.content.decode(encoding))
        self.assertEqual(data['status'], 'error')
        self.assertEqual(data['code'], code)


    def check_ajax_processing(self, response, status_url=None, content_type='application/json', encoding='utf-8'):
        self.assertTrue(content_type in response['Content-Type'])
        self.assertTrue(encoding in response['Content-Type'])

        self.assertEqual(response.status_code, 200)
        data = s11n.from_json(response.content.decode(encoding))
        self.assertEqual(data['status'], 'processing')
        if status_url:
            self.assertEqual(data['status_url'], status_url)

    def check_js_ok(self, response, status_code=200, texts=[], content_type='application/x-javascript', encoding='utf-8', body=None):
        self.check_html_ok(response, status_code=status_code, texts=texts, content_type=content_type, encoding=encoding)

    def check_redirect(self, requested_url, test_url, status_code=302, target_status_code=200):
        self.check_response_redirect(self.request_html(requested_url), test_url, status_code=status_code, target_status_code=target_status_code)

    def check_response_redirect(self, response, test_url, status_code=302, target_status_code=200):
        self.assertRedirects(response, test_url, status_code=status_code, target_status_code=target_status_code)

    @contextlib.contextmanager
    def check_not_changed(self, callback):
        old_value = callback()
        yield
        self.assertEqual(callback(), old_value)

    @contextlib.contextmanager
    def check_changed(self, callback):
        old_value = callback()
        yield
        self.assertNotEqual(callback(), old_value)

    @contextlib.contextmanager
    def check_delta(self, callback, delta):
        old_value = callback()
        yield
        self.assertEqual(callback() - old_value, delta)

    @contextlib.contextmanager
    def check_increased(self, callback):
        old_value = callback()
        yield
        self.assertTrue(callback() > old_value)

    @contextlib.contextmanager
    def check_decreased(self, callback):
        old_value = callback()
        yield
        self.assertTrue(callback() < old_value)

    def check_serialization(self, obj):
        obj_data = obj.serialize()
        self.assertEqual(obj_data, obj.deserialize(s11n.from_json(s11n.to_json(obj_data))).serialize())

    def request_html(self, url):
        return self.client.get(url, HTTP_ACCEPT='text/html')

    def request_js(self, url):
        return self.client.get(url, HTTP_ACCEPT='application/x-javascript')

    def request_xml(self, url):
        return self.client.get(url, HTTP_ACCEPT='text/xml')

    def request_json(self, url):
        return self.client.get(url, HTTP_ACCEPT='text/json')

    def request_ajax_json(self, url):
        return self.client.get(url, HTTP_ACCEPT='text/json', HTTP_X_REQUESTED_WITH='XMLHttpRequest')

    def request_ajax_html(self, url):
        return self.client.get(url, HTTP_ACCEPT='text/html', HTTP_X_REQUESTED_WITH='XMLHttpRequest')

    def post_xml(self, url):
        return self.client.post(url, HTTP_ACCEPT='text/xml')

    def post_html(self, url):
        return self.client.post(url, HTTP_ACCEPT='text/html')

    def post_ajax_html(self, url, data=None):
        return self.client.post(url, data if data else {}, HTTP_ACCEPT='text/html', HTTP_X_REQUESTED_WITH='XMLHttpRequest')

    def post_ajax_json(self, url, data=None):
        return self.client.post(url, data if data else {}, HTTP_ACCEPT='text/json', HTTP_X_REQUESTED_WITH='XMLHttpRequest')

    @make_request_decorator
    def make_request_html(self, url, meta={}):
        _meta = {'HTTP_ACCEPT': 'text/html'}
        _meta.update(meta)
        return self.request_factory.get(url, **_meta)

    @make_request_decorator
    def make_request_xml(self, url, meta={}):
        _meta = {'HTTP_ACCEPT': 'text/xml'}
        _meta.update(meta)
        return self.request_factory.get(url, **_meta)

    @make_request_decorator
    def make_request_ajax_json(self, url, meta={}):
        _meta = {'HTTP_ACCEPT': 'text/json',
                 'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}
        _meta.update(meta)
        return self.request_factory.get(url, **_meta)

    @make_request_decorator
    def make_request_ajax_html(self, url, meta={}):
        _meta = {'HTTP_ACCEPT': 'text/html',
                 'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}
        _meta.update(meta)
        return self.request_factory.get(url, **_meta)

    @make_request_decorator
    def make_post_xml(self, url, meta={}):
        _meta = {'HTTP_ACCEPT': 'text/xml'}
        _meta.update(meta)
        return self.request_factory.post(url, **_meta)

    @make_request_decorator
    def make_post_ajax_json(self, url, data=None, meta={}):
        _meta = {'HTTP_ACCEPT': 'text/json',
                 'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}
        _meta.update(meta)
        return self.request_factory.post(url, data if data else {}, **_meta)


class TestCase(DjangoTestCase, TestCaseMixin):
    def setUp(self):
        self.request_factory = RequestFactory()

    def tearDown(self):
        pass


class TransactionTestCase(DjangoTransactionTestCase, TestCaseMixin):
    def setUp(self):
        self.request_factory = RequestFactory()

    def tearDown(self):
        pass
