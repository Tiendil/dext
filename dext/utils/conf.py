# coding: utf-8
import os

from dext.utils.app_settings import app_settings

utils_settings = app_settings('DEXT',
                              PID_DIRECTORY=os.getenv("HOME"),
                              PID_DIRECTORY_MODE=0755)
