# coding: utf-8
from dext.jinja2.decorators import jinjaglobal
from dext.common.utils import urls


@jinjaglobal
def url(*args, **kwargs): return urls.url(*args, **kwargs)

@jinjaglobal
def full_url(*args, **kwargs): return urls.full_url(*args, **kwargs)

@jinjaglobal
def absolute_url(*args, **kwargs): return urls.absolute_url(*args, **kwargs)
