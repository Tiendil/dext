# coding: utf-8
import functools
import cProfile

# _pr = cProfile.Profile()
# _CALIBRATE_VALUE = _pr.calibrate(1000000)


def profile_decorator(output_file):

    def decorator(func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):

            prof = cProfile.Profile()
            try:
                ret = prof.runcall(func, *args, **kwargs)
            except:
                ret = None

            prof.dump_stats(output_file)

            return ret

        return wrapper

    return decorator
