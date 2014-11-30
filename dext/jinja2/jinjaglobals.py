# coding: utf-8
import datetime
import time
import collections

import jinja2


from .decorators import jinjafilter, jinjaglobal


@jinjaglobal
def jmap(func, iterable):
    return map(func, iterable)

@jinjaglobal
@jinja2.contextfunction
def get_context(context):
    return context


@jinjafilter
def endl2br(value):
    return jinja2.Markup(value.replace('\n\r', '</br>').replace('\n', r'</br>'))

@jinjafilter
def percents(value, points=0):
    return ('%'+('.%d' % points) + 'f%%') % (round(value, 2+points) * 100)

@jinjafilter
def timestamp(value):
    return time.mktime(value.timetuple())

@jinjaglobal
def now():
    return datetime.datetime.now()

@jinjafilter
def up_first(value):
    if value:
        return value[0].upper() + value[1:]
    return value

@jinjaglobal
def is_sequence(variable):
    return not isinstance(variable, basestring) and isinstance(variable, collections.Iterable)
