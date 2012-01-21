# -*- coding: utf-8 -*-
import functools

from ..jinja2 import render


def template_renderer(template_name, context={}):

    @functools.wraps(template_renderer)
    def view(request):
        return render.template(template_name, context, request)

    return view
        

