# coding: utf-8

from datetime import datetime

from dext.settings.conf import dext_settings_settings


class SettingsException(Exception): pass


class Settings(object):

    def __init__(self):
        self.data = {}
        self.initialized = False

    def _load_data(self):
        from dext.settings import models
        return dict(models.Setting.objects.all().values_list('key', 'value'))
        # return {record.key:record.value for record in Setting.objects.all()}

    def refresh(self, force=False):
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
        from dext.settings import models

        if not isinstance(key, basestring):
            raise SettingsException('wrong key type: %r' % key)
        if not isinstance(value, basestring):
            raise SettingsException('wrong value type: %r' % value)

        if not self.initialized:
            self.refresh()

        if dext_settings_settings.UPDATE_DATABASE:
            if key in self.data:
                models.Setting.objects.filter(key=key).update(value=value, updated_at=datetime.now())
            else:
                models.Setting.objects.create(key=key, value=value)

        self.data[key] = value

    def __delitem__(self, key):
        from dext.settings import models

        if not isinstance(key, basestring):
            raise SettingsException('wrong key type: %r' % key)

        if not self.initialized:
            self.refresh()

        if key in self.data:
            models.Setting.objects.filter(key=key).delete()
        else:
            raise SettingsException('key "%r" not in settings' % key)

        del self.data[key]

    def __contains__(self, key):

        if not self.initialized:
            self.refresh()

        return key in self.data

    def get(self, key, default=None):
        if key in self:
            return self[key]
        return default


settings = Settings()
