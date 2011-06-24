# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.template import RequestContext

from .. import jinja2 as jinja2_next

def template(template_name, context, request, mimetype='text/html'):
    request_context = RequestContext(request, context)

    jinja_context = {}
    for d in request_context:
        jinja_context.update(d)

    response = HttpResponse(jinja2_next.render(template_name, jinja_context), mimetype=mimetype)
    return response
