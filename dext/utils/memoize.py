# coding: utf-8
import functools


def memclass(function):

    cache_name = '_%s' % function.__name__

    @functools.wraps(function)
    def wrapper(cls, *args, **kwargs):
        if not hasattr(cls, cache_name):
            setattr(cls, cache_name, function(cls, *args, **kwargs))
        return getattr(cls, cache_name)

    return wrapper
