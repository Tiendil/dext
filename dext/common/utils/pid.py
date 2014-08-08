# coding: utf-8
import os
import signal
import functools

from dext.common.utils.conf import utils_settings

# TODO: make an atomic operations (see, lockfile package)

def capture(uuid, directory=utils_settings.PID_DIRECTORY, directory_mode=utils_settings.PID_DIRECTORY_MODE):

    if not os.path.exists(directory):
        os.makedirs(directory, mode=directory_mode)

    pid_file = os.path.join(directory, uuid + '.pid')

    if os.path.exists(pid_file):
        return False

    pid = os.getpid()

    with open(pid_file, 'w') as f:
        f.write('%d\n' % pid)

    return True


def check(uuid, directory=utils_settings.PID_DIRECTORY):
    pid_file = os.path.join(directory, uuid + '.pid')
    return os.path.exists(pid_file)


def free(uuid, directory=utils_settings.PID_DIRECTORY):
    pid_file = os.path.join(directory, uuid + '.pid')
    os.remove(pid_file)

def get(uuid, directory=utils_settings.PID_DIRECTORY):
    if not check(uuid, directory):
        return None

    pid_file = os.path.join(directory, uuid + '.pid')

    pid = None

    try:
        with open(pid_file, 'r') as f:
            pid = int(f.read())
    except:
        pass

    return pid


def protector(uuid, directory=utils_settings.PID_DIRECTORY, directory_mode=utils_settings.PID_DIRECTORY_MODE):

    def decorator(func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not capture(uuid, directory, directory_mode):
                print 'process has been already running'
                return

            try:
                func(*args, **kwargs)
            finally:
                free(uuid, directory)

        return wrapper

    return decorator


def force_kill(uid, directory=utils_settings.PID_DIRECTORY):
    process_id = get(uid, directory)

    if process_id is not None:
        try:
            os.kill(process_id, signal.SIGKILL)
        except OSError:
            pass
        free(uid, directory)
