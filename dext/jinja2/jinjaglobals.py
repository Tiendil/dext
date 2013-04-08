# coding: utf-8
import datetime
import time
import jinja2

from dext.jinja2.decorators import jinjafilter, jinjaglobal
from dext.utils import urls

@jinjaglobal
def url(*args, **kwargs): return urls.url(*args, **kwargs)

@jinjaglobal
def full_url(*args, **kwargs): return urls.full_url(*args, **kwargs)

@jinjaglobal
def absolute_url(*args, **kwargs): return urls.absolute_url(*args, **kwargs)

@jinjaglobal
def jmap(func, iterable):
    return map(func, iterable)


@jinjafilter
def endl2br(value):
    return jinja2.Markup(value.replace('\n\r', '</br>').replace('\n', r'</br>'))

@jinjafilter
def percents(value):
    return '%d%%' % int((round(value, 2) * 100))

@jinjafilter
def timestamp(value):
    return time.mktime(value.timetuple())

@jinjaglobal
def now():
    return datetime.datetime.now()
