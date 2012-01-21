# -*- coding: utf-8 -*-
import jinja2
from django import forms
from . import pgf_widgets

class FormsException(Exception): pass 

def errors_container(self): 
    return jinja2.Markup('<div class="pgf-form-field-marker-%s pgf-error-container error-container"></div>' % self.name)

def widget(self):
    html = jinja2.Markup(self.label_tag()) + jinja2.Markup(self) + self.errors_container
    template = jinja2.Markup(u'<div data-widget-name="%(name)s" data-widget-type="%(type)s" class="pgf-widget widget">%(content)s</div>')
    html =  template % {'content': html,
                        'name': self.name,
                        'type': self.field.pgf['type'] if 'type' in self.field.pgf else ''}
    html = jinja2.Markup(html)
    return html

def pgf_widget(self):
    try:
        html = pgf_widgets.widgets[self.field.pgf['type']](self)
    except Exception, e:
        raise FormsException(unicode(e))
    return jinja2.Markup(html)

forms.forms.BoundField.errors_container = property(errors_container)
forms.forms.BoundField.widget = property(widget)
forms.forms.BoundField.pgf_widget = property(pgf_widget)


class CleanedDataAccessor(object):

    def __init__(self, form):
        self.form = form

    def __getattr__(self, name):
        if name in self.form.cleaned_data:
            return self.form.cleaned_data[name]
        raise FormsException('can not get cleaned data - wrong field name "%s"' % name)

    @property
    def data(self):
        return self.form.cleaned_data


class Form(forms.Form):

    def __iter__(self):
        return super(Form, self).__iter__()
	
    def __getitem__(self, name):
        return super(Form, self).__getitem__(name)

    @property
    def errors_container(self): 
        return jinja2.Markup('<div class="pgf-form-marker pgf-error-container error-container"></div>')


    @property
    def c(self):
        if not hasattr(self, '_c'):
            self._c = CleanedDataAccessor(self)
        return self._c
        
