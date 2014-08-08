
from django.conf import settings as project_settings

class AppSettings(object): pass

def app_settings(prefix, **kwargs):
    settings = AppSettings()

    for key, default_value in kwargs.items():
        project_key = '%s_%s' % (prefix, key)
        if hasattr(project_settings, project_key):
            setattr(settings, key, getattr(project_settings, project_key))
        else:
            setattr(settings, key, default_value)

    return settings
