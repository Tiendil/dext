# coding: utf-8

from dext.views.resources import BaseResource, handler


class EmptyResourceTestClass(BaseResource):

    def initialize(self):
        super(ResourceTestClass, self).initialize()



class ResourceTestClass(BaseResource):

    def initialize(self):
        super(ResourceTestClass, self).initialize()

    @handler('')
    def index(self):
        pass

    @handler('#object_id', 'show')
    def show(self):
        pass
