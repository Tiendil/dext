# -*- coding: utf-8 -*-
import functools

from django.db import transaction

def nested_commit_on_success(func):

    commit_on_success = transaction.commit_on_success(func)

    @functools.wraps(func)
    def _nested_commit_on_success(*args, **kwds):
        if transaction.is_managed():
            return func(*args,**kwds)
        else:
            return commit_on_success(*args,**kwds)
    return transaction.wraps(func)(_nested_commit_on_success)
