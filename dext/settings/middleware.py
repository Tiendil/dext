# coding: utf-8

from dext.settings import settings

class SettingsMiddleware(object):

    def process_request(self, request):
        settings.refresh()
