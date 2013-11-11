from django.conf.urls import patterns, url

from dext.less.views import less_compiler

urlpatterns = patterns('',
                       url(r'^(?P<path>.*).css$', less_compiler),
)
