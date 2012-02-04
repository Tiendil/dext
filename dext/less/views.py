# Create your views here.
import os
from subprocess import Popen, PIPE

from django.http import HttpResponse
from django.conf import settings
from django.views.decorators.cache import never_cache

@never_cache
def less_compiler(request, path):

    file_path = os.path.join(settings.LESS_FILES_DIR, path + '.less')
    if not os.path.exists(file_path):
        file_path = os.path.join(settings.LESS_FILES_DIR, path + '.css')
    
    (out, err) = Popen(["lessc", file_path], stdout=PIPE).communicate()
    
    return HttpResponse(out, mimetype='text/css')
