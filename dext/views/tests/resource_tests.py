# coding: utf-8

from django.core.urlresolvers import reverse

from dext.utils import s11n
from dext.utils.testcase import TestCase

from dext.views.tests.helpers import ResourceTestClass


class ResourceTests(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_init(self):
        fake_request = self.fake_request(csrf='some-csrf-token')
        resource = ResourceTestClass(fake_request)
        self.assertEqual(resource.request, fake_request)
        self.assertEqual(resource.csrf, 'some-csrf-token')

    def test_get_handlers(self):
        self.assertEqual('not implemented', False)

    def test_string(self):
        resource = ResourceTestClass(self.fake_request())
        self.check_html_ok(resource.string('some string'), texts=['some string'], content_type='text/html', encoding='utf-8')

    def test_atom(self):
        resource = ResourceTestClass(self.fake_request())
        self.check_html_ok(resource.atom('some string'), texts=['some string'], content_type='application/atom+xml', encoding='utf-8')

    def test_rss(self):
        resource = ResourceTestClass(self.fake_request())
        self.check_html_ok(resource.rss('some string'), texts=['some string'], content_type='application/rss+xml', encoding='utf-8')

    def test_rdf(self):
        resource = ResourceTestClass(self.fake_request())
        self.check_html_ok(resource.rdf('some string'), texts=['some string'], content_type='application/rdf+xml', encoding='utf-8')

    def test_json(self):
        resource = ResourceTestClass(self.fake_request())
        self.check_html_ok(resource.json(data={'id': 'some text'}), texts=['data', 'some text', 'id'], content_type='application/json', encoding='utf-8')

    def test_json_ok(self):
        resource = ResourceTestClass(self.fake_request())
        self.check_ajax_ok(resource.json_ok({'id': 'some text'}), {'id': 'some text'}, content_type='application/json', encoding='utf-8')

    def test_json_processing(self):
        resource = ResourceTestClass(self.fake_request())
        self.check_ajax_processing(resource.json_processing('some/url'), 'some/url', content_type='application/json', encoding='utf-8')

    def test_json_error(self):
        resource = ResourceTestClass(self.fake_request())
        self.check_ajax_error(resource.json_error('some.error.code', u'error text'), 'some.error.code', content_type='application/json', encoding='utf-8')

    def test_json_errors(self):
        resource = ResourceTestClass(self.fake_request())
        self.check_ajax_error(resource.json_error('some.error.code', [u'error text']), 'some.error.code', content_type='application/json', encoding='utf-8')

    def test_css(self):
        resource = ResourceTestClass(self.fake_request())
        self.check_html_ok(resource.css('some text'), texts=['some text'], content_type='text/css', encoding='utf-8')

    def test_redirect(self):
        self.assertEqual('not implemented', False)

    def test_auto_error(self):
        self.assertEqual('not implemented', False)
