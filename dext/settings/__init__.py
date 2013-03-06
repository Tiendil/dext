# coding: utf-8

from dext.utils import cache
from dext.settings.models import Setting
from dext.settings.conf import dext_settings

class SettingsException(Exception): pass


class Settings(object):

    def __init__(self):
        self.data = {}
        self.initialized = False

    @cache.memoize(dext_settings.CACHE_KEY, dext_settings.CACHE_TIME)
    def _load_data(self):
        return {record.key:record.value for record in Setting.objects.all()}

    def _cache_data(self):
        cache.set(dext_settings.CACHE_KEY, self.data, dext_settings.CACHE_TIME)

    def refresh(self):
        self.initialized = True
        self.data = self._load_data()

    def __getitem__(self, key):
        if not isinstance(key, basestring):
            raise SettingsException('wrong key type: %r' % key)
        if not key in self.data:
            raise SettingsException('unregistered key: %s' % key)

        if not self.initialized:
            self.refresh()

        return self.data[key]

    def __setitem__(self, key, value):

        if not isinstance(key, basestring):
            raise SettingsException('wrong key type: %r' % key)
        if not isinstance(value, basestring):
            raise SettingsException('wrong value type: %r' % value)

        if not self.initialized:
            self.refresh()

        if key in self.data:
            Setting.objects.filter(key=key).update(value=value)
        else:
            Setting.objects.create(key=key, value=value)

        self.data[key] = value

        self._cache_data()

    def __contains__(self, key):

        if not self.initialized:
            self.refresh()

        return key in self.data

    def get(self, key, default=None):
        if key in self:
            return self[key]
        return default


settings = Settings()
