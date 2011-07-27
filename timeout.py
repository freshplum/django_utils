import signal
from django.conf import settings

from misc import CustomError

def handler(signum, frame):
    raise CustomError("Timeout")

if not settings.DEBUG:
    signal.signal(signal.SIGALRM, handler)

def run_func(timeout, func, *args, **kwargs):
    """
    This will run the function passed.
    And will raise an exception if the
    the function takes more than timeout
    (specified in miliseconds).

    """

    signal.setitimer(signal.ITIMER_REAL, float(timeout)/1000.0)
    result = func(*args, **kwargs)
    signal.setitimer(signal.ITIMER_REAL, 0)
    return result