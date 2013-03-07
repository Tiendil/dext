# coding: utf-8

import functools

from django.core.cache import cache as django_cache

def set(key, value, timeout):
    django_cache.set(key, value, timeout)

def get(key):
    return django_cache.get(key)

def set_many(cache_dict, timeout):
    django_cache.set_many(cache_dict, timeout)

def memoize(key, timeout):

    @functools.wraps(memoize)
    def decorator(function):

        @functools.wraps(function)
        def wrapper(*argv, **kwargs):

            data = django_cache.get(key)

            if data is not None:
                return data

            data = function(*argv, **kwargs)

            django_cache.set(key, data, timeout)

            return data

        return wrapper

    return decorator
