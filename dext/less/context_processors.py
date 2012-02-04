from django.conf import settings

def less(request):
    return {'LESS_CSS_URL': settings.LESS_CSS_URL}
