# coding: utf-8

from dext.settings import settings


class SettingsMiddleware(object):

    def __init__(self, get_response):
        self.get_response = get_response


    def __call__(self, request):
        settings.refresh()

        return self.get_response(request)
