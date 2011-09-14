# -*- coding: utf-8 -*-
import functools

from django.db import transaction
from django.conf import settings as project_settings
from django.http import Http404

def nested_commit_on_success(func):

    commit_on_success = transaction.commit_on_success(func)

    @functools.wraps(func)
    def _nested_commit_on_success(*args, **kwds):
        if transaction.is_managed():
            return func(*args,**kwds)
        else:
            return commit_on_success(*args,**kwds)
    return transaction.wraps(func)(_nested_commit_on_success)


def staff_required(permissions=[]):

    @functools.wraps(staff_required)
    def decorator(func):
        @functools.wraps(func)
        def wrapper(resource, *argv, **kwargs):
            if permissions:
                raise NotImplemented('staff required decorator has not emplimented for working woth permissions list')
            else:
                if resource.request.user.is_active and resource.request.user.is_staff:
                    return func(resource, *argv, **kwargs)
                else: 
                    if resource.request.is_ajax() or resource.request.method.lower() == 'post':
                        return resource.json(status='error',
                                             error=u'У Вас нет прав для проведения данной операции')
                    return resource.redirect('accounts:login')

        return wrapper

    return decorator

    
def debug_required(func):
    
    @functools.wraps(func)
    def wrapper(resource, *argv, **kwargs):
        if project_settings.DEBUG:
            return func(resource, *argv, **kwargs)
        raise Http404()

    return wrapper

    


