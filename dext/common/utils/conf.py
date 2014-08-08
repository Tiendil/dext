# coding: utf-8
from dext.common.utils.app_settings import app_settings

utils_settings = app_settings('DEXT',
                              PID_DIRECTORY='/tmp',
                              PID_DIRECTORY_MODE=0755)
