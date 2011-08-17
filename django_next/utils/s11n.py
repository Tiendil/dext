# -*- coding: utf-8 -*-
import json
from django.conf import settings as project_settings

def to_json(data):
    if project_settings.DEBUG:
        return json.dumps(data, ensure_ascii=False, check_circular=True, allow_nan=False, indent=2)
    else:
        return json.dumps(data, ensure_ascii=False, check_circular=False, allow_nan=False, indent=0)

def from_json(data):
    return json.loads(data)
