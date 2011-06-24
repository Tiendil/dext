from django.conf.urls.defaults import patterns, url

from .views import less_compiler

urlpatterns = patterns('',
                       url(r'^(?P<path>.*).css$', less_compiler),
)
