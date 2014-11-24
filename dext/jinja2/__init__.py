# coding: utf-8

from dext.jinja2.renderer import get_jinjaglobals, render


def autodiscover():

    from django.conf import settings as project_settings
    from django.utils.importlib import import_module
    from django.utils.module_loading import module_has_submodule

    for app in project_settings.INSTALLED_APPS:
        mod = import_module(app)

        try:
            jinjaglobals = import_module('%s.jinjaglobals' % app)

            global_functions, filter_functions = get_jinjaglobals(jinjaglobals)

            render.update_globals(global_functions, filter_functions)
        except:
            if module_has_submodule(mod, 'jinjaglobals'):
                raise
