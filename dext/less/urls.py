from django.conf.urls import url

from dext.less.views import less_compiler

urlpatterns = [url(r'^(?P<path>.*).css$', less_compiler)]
