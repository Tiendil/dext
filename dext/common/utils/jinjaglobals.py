# coding: utf-8
from __future__ import absolute_import

from dext.common.utils import jinja2
from dext.common.utils import urls

import datetime
import time
import collections


@jinja2.jinjaglobal
def jmap(func, *iterables):
    return map(func, *iterables)

@jinja2.jinjaglobal
@jinja2.contextfunction
def get_context(context):
    return context


@jinja2.jinjafilter
def endl2br(value):
    return jinja2.Markup(value.replace('\n\r', '</br>').replace('\n', r'</br>'))

@jinja2.jinjafilter
def percents(value, points=0):
    return ('%'+('.%d' % points) + 'f%%') % (round(value, 2+points) * 100)

@jinja2.jinjafilter
def timestamp(value):
    return time.mktime(value.timetuple())

@jinja2.jinjaglobal
def now():
    return datetime.datetime.now()

@jinja2.jinjafilter
def up_first(value):
    if value:
        return value[0].upper() + value[1:]
    return value

@jinja2.jinjaglobal
def is_sequence(variable):
    return not isinstance(variable, basestring) and isinstance(variable, collections.Iterable)

@jinja2.jinjaglobal
def url(*args, **kwargs): return urls.url(*args, **kwargs)

@jinja2.jinjaglobal
def full_url(*args, **kwargs): return urls.full_url(*args, **kwargs)

@jinja2.jinjaglobal
def absolute_url(*args, **kwargs): return urls.absolute_url(*args, **kwargs)
