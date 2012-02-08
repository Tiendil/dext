# -*- coding: utf-8 -*-
import time
import jinja2
import urllib
 
from django.core.urlresolvers import reverse

from .decorators import jinjafilter, jinjaglobal

@jinjaglobal
def url(*args, **kwargs):
    base_url = reverse(args[0], args=args[1:])
    if kwargs:
        query = urllib.urlencode(kwargs)
        base_url = '%s?%s' % (base_url, query)
    return base_url


@jinjafilter
def endl2br(value):
    return jinja2.Markup(value.replace('\n\r', '</br>').replace('\n', r'</br>'))

@jinjafilter
def percents(value):
    return '%d%%' % int((round(value, 2) * 100))

@jinjafilter
def timestamp(value):
    return time.mktime(value.timetuple())
