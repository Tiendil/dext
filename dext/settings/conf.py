# coding: utf-8

from dext.utils.app_settings import app_settings


dext_settings = app_settings('DEXT_SETTINGS',
                             CACHE_KEY='dext_settings',
                             CACHE_TIME=24*60*60   )
