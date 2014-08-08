# coding: utf-8
import functools

from django.conf import settings as project_settings
from django.http import Http404


def debug_required(func):

    @functools.wraps(func)
    def wrapper(resource, *argv, **kwargs):
        if project_settings.DEBUG:
            return func(resource, *argv, **kwargs)
        raise Http404()

    return wrapper


def retry_on_exception(max_retries=None, exceptions=[Exception]):

    @functools.wraps(retry_on_exception)
    def decorator(func):

        @functools.wraps(func)
        def wrapper(*argv, **kwargs):
            retries_number = 0
            while True:
                retries_number += 1
                try:
                    return func(*argv, **kwargs)
                except Exception, e:

                    if retries_number == max_retries:
                        raise

                    found = False
                    for exception in exceptions:
                        if isinstance(e, exception):
                            found = True

                    if not found:
                        raise



        return wrapper

    return decorator
