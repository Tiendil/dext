# coding: utf-8
import datetime
import time
import jinja2
import urllib

from django.conf import settings as project_settings
from django.core.urlresolvers import reverse

from .decorators import jinjafilter, jinjaglobal

@jinjaglobal
def url(*args, **kwargs):
    base_url = reverse(args[0], args=args[1:])
    if kwargs:
        query = urllib.urlencode(kwargs)
        base_url = '%s?%s' % (base_url, query)
    return base_url

@jinjaglobal
def full_url(protocol, *args, **kwargs):
    return protocol + '://' + project_settings.SITE_URL + url(*args, **kwargs)

@jinjaglobal
def absolute_url(relative_url, protocol='http'):
    return protocol + '://' + project_settings.SITE_URL + relative_url

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
