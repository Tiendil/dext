# -*- coding: utf-8 -*-
import jinja2


from django.conf import settings as project_settings
from django.http import HttpResponse
from django.template import RequestContext

from .conf import settings as jinja2_settings
from . import jinjaglobals

def get_jinjaglobals(module):

    filter_functions = {}
    global_functions = {}

    for func_name in dir(module):
        func = getattr(module, func_name)

        if getattr(func, '_is_jinjaglobal', False):
            global_functions[func_name] = func

        if getattr(func, '_is_jinjafilter', False):
            filter_functions[func_name] = func

    return global_functions, filter_functions



class Jinja2Renderer(object):

    def __init__(self, settings):

        #form templates loaders
        filesystem_loader = jinja2.FileSystemLoader(jinja2_settings.TEMPLATE_DIRS)

        apps_loader_params = {}

        # use last application_name part as unique name, since django expect it's uniqueness
        for application_name in settings.INSTALLED_APPS:
            apps_loader_params[application_name.split('.')[-1]] = jinja2.PackageLoader(application_name)

        apps_loader = jinja2.PrefixLoader(apps_loader_params)

        loader = jinja2.ChoiceLoader([filesystem_loader, apps_loader])

        self.env = jinja2.Environment(loader=loader,
                                      autoescape=True,
                                      trim_blocks=True,
                                      auto_reload=settings.DEBUG)

    def update_globals(self, global_functions, filter_functions):
        self.env.globals.update(global_functions)
        self.env.filters.update(filter_functions)

    def __call__(self, template_name, content={}):

        template = self.env.get_template(template_name)

        text = template.render(content)

        return text

    def template(self, template_name, context={}, request=None):
        jinja_context = context

        context['request'] = request
        context['settings'] = project_settings

        if request:
            jinja_context = {}

            request_context = RequestContext(request, context)

            for d in request_context:
                jinja_context.update(d)

        return self(template_name, jinja_context)


render = Jinja2Renderer(project_settings)
global_functions, filter_functions = get_jinjaglobals(jinjaglobals)
render.update_globals(global_functions, filter_functions)
