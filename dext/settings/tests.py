# coding: utf-8
import mock

from dext.utils import testcase
from dext.settings import Settings, SettingsException
from dext.settings.models import Setting


class SettingsTest(testcase.TestCase):

    def setUp(self):
        self.settings = Settings()

    def test_set_wrong_key(self):
        self.assertRaises(SettingsException, self.settings.__setitem__, 1, 'value')

    def test_set_wrong_value(self):
        self.assertRaises(SettingsException, self.settings.__setitem__, 'key', 1)

    def test_set_with_create(self):
        self.assertEqual(Setting.objects.all().count(), 0)

        with mock.patch('dext.settings.Settings._cache_data') as counter:
            self.settings['key'] = 'value'

        self.assertEqual(counter.call_count, 1)
        self.assertEqual(Setting.objects.all().count(), 1)

        record = Setting.objects.all()[0]
        self.assertEqual(record.key, 'key')
        self.assertEqual(record.value, 'value')

    def test_set_without_create(self):

        self.assertEqual(Setting.objects.all().count(), 0)

        with mock.patch('dext.settings.Settings._cache_data') as counter:
            self.settings['key'] = 'value'
            self.assertEqual(Setting.objects.all().count(), 1)
            self.settings['key'] = 'value 2'

        self.assertEqual(counter.call_count, 2)
        self.assertEqual(Setting.objects.all().count(), 1)

        record = Setting.objects.all()[0]
        self.assertEqual(record.key, 'key')
        self.assertEqual(record.value, 'value 2')

    def test_get_wrong_key(self):
        self.settings['key'] = 'value'
        self.assertRaises(SettingsException, self.settings.__getitem__, 1)

    def test_get_no_value(self):
        self.settings['key'] = 'value'
        self.assertRaises(SettingsException, self.settings.__getitem__, 'unknown key')

    def test_get(self):
        self.settings['key'] = 'value'
        self.assertEqual(self.settings['key'], 'value')

    def test_refresh(self):
        Setting.objects.create(key='key 1', value='value 1')
        Setting.objects.create(key=u'ключ 2', value=u'значение 2')
        self.settings.refresh()
        self.assertEqual(self.settings['key 1'], 'value 1')
        self.assertEqual(self.settings[u'ключ 2'], u'значение 2')
