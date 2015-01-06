# coding: utf-8
import os
import functools

from django.conf import settings as project_settings
from django.utils.importlib import import_module
from django.utils.module_loading import module_has_submodule


def is_module_exists(module_path):
    try:
        return import_module(module_path)
    except StandardError:
        return False


def discover_classes(classes_list, base_class):
    return ( class_
             for class_ in classes_list
             if isinstance(class_, type) and issubclass(class_, base_class) and class_ != base_class)


def module_variables(module):
    for name in dir(module):
        yield getattr(module, name)


def discover_classes_in_module(module, base_class):
    return discover_classes(module_variables(module), base_class)


def automatic_discover(container, module_name):

    @functools.wraps(automatic_discover)
    def decorator(function):

        @functools.wraps(function)
        def wrapper(if_empty=False):
            if container and if_empty:
                return

            container.clear()

            for app in project_settings.INSTALLED_APPS:
                mod = import_module(app)

                try:
                    function(container, import_module('%s.%s' % (app, module_name)))
                except StandardError:
                    if module_has_submodule(mod, module_name):
                        raise

        return wrapper

    return decorator


def get_function(function_path):
    module_path, function_name = function_path.rsplit('.', 1)
    module = import_module(module_path)
    return getattr(module, function_name)


def discover_modules_in_directory(path, prefix, exclude=('__init__.py',)):

    for name in os.listdir(path):
        if not name.endswith('.py'):
            continue

        if name in exclude:
            continue

        yield import_module('%s.%s' % (prefix, name[:-3]))
