# coding: utf-8
import os

from dext.utils.conf import utils_settings

def capture(uuid, directory=utils_settings.PID_DIRECTORY, directory_mode=utils_settings.PID_DIRECTORY_MODE):

    if not os.path.exists(directory):
        os.makedirs(directory, mode=directory_mode)

    pid_file = os.path.join(directory, uuid + '.pid')

    if os.path.exists(pid_file):
        return False

    with open(pid_file, 'w') as f:
        f.write('%d' % os.getpid())

    return True


def check(uuid, directory=utils_settings.PID_DIRECTORY):
    pid_file = os.path.join(directory, uuid + '.pid')
    return os.path.exists(pid_file)
