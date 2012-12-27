# coding: utf-8

from dext.views.resources import BaseResource, handler


class ResourceTestClass(BaseResource):

    def initialize(self):
        super(ResourceTestClass, self).initialize()
