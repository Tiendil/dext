# coding: utf-8
import os
from contextlib import contextmanager

from dext.utils.conf import utils_settings

def capture(uuid, directory=utils_settings.PID_DIRECTORY, directory_mode=utils_settings.PID_DIRECTORY_MODE):

    if not os.path.exists(directory):
        os.makedirs(directory, mode=directory_mode)

    pid_file = os.path.join(directory, uuid + '.pid')

    if os.path.exists(pid_file):
        return False

    with open(pid_file, 'w') as f:
        f.write('%d\n' % os.getpid())

    return True


def check(uuid, directory=utils_settings.PID_DIRECTORY):
    pid_file = os.path.join(directory, uuid + '.pid')
    return os.path.exists(pid_file)


def free(uuid, directory=utils_settings.PID_DIRECTORY):
    pid_file = os.path.join(directory, uuid + '.pid')
    os.remove(pid_file)


@contextmanager
def wrap(uuid, directory=utils_settings.PID_DIRECTORY, directory_mode=utils_settings.PID_DIRECTORY_MODE):
    if not capture(uuid, directory, directory_mode):
        print 'process has been already running'
        yield
        return

    yield
    free(uuid, directory)
