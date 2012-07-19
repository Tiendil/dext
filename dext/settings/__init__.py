# coding: utf-8

from dext.settings.models import Setting

class SettingsException(Exception): pass


class Settings(object):

    def __init__(self):
        self.data = {}
        self.initialized = False

    def refresh(self):
        self.initialized = True
        self.data = dict([ (record.key, record) for record in Setting.objects.all()])

    def __getitem__(self, key):
        if not isinstance(key, basestring):
            raise SettingsException('wrong key type: %r' % key)
        if not key in self.data:
            raise SettingsException('unregistered key: %s' % key)

        if not self.initialized:
            self.refresh()

        return self.data[key].value

    def __setitem__(self, key, value):

        if not isinstance(key, basestring):
            raise SettingsException('wrong key type: %r' % key)
        if not isinstance(value, basestring):
            raise SettingsException('wrong value type: %r' % value)

        if not self.initialized:
            self.refresh()

        if key in self.data:
            record = self.data[key]
            record.value = value
            record.save()
            return

        record = Setting(key=key, value=value)
        record.save()
        self.data[key] = record

    def __contains__(self, key):

        if not self.initialized:
            self.refresh()

        return key in self.data

    def get(self, key, default=None):
        if key in self:
            return self[key]
        return default


settings = Settings()
