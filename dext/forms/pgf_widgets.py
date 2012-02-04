# -*- coding: utf-8 -*-

def static_value(bound_field):
    template = '''
<div class="pgf-widget" data-widget-type="static-value" data-widget-name="%(name)s">
    %(label_tag)s
    <input class="pgf-value" type="hidden" value="%(value)s" name="%(name)s"/>
    <span class="pgf-displayed-value">%(value)s</span>
    <div class="pgf-form-field-marker-%(name)s pgf-error-container"></div>
</div>''' 

    result = template % {'name': bound_field.html_name,
                         'label_tag': bound_field.label_tag(),
                         'value': bound_field.value() }
    return result


def integer_interval(bound_field):
    template = '''
<div class="pgf-widget" 
     data-widget-type="integer-interval" 
     data-widget-name="%(name)s"
     %(interval-min)s
     %(interval-max)s
     %(limited-by)s>
    %(label_tag)s
    <input type="button" class="pgf-minus" value="-">
    <input class="pgf-value" type="text" value="%(value)s" name="%(name)s" size="2"/>
    <input type="button" class="pgf-plus" value="+">
    <div class="pgf-form-field-marker-%(name)s pgf-error-container"></div>
</div>''' 

    interval_min = 'data-interval-min="%s"' % bound_field.field.min_value
    interval_max = 'data-interval-max="%s"' % bound_field.field.max_value
    limited_by = 'data-limited-by="%s"' % bound_field.field.pgf['limited-by']

    result = template % {'name': bound_field.html_name,
                         'label_tag': bound_field.label_tag(),
                         'value': bound_field.value(),
                         'interval-min': interval_min,
                         'interval-max': interval_max,
                         'limited-by': limited_by}
    return result


widgets = {'static-value': static_value,
           'integer-interval': integer_interval}
