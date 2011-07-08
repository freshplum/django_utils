import time
import logging
import inspect

from django.core.mail import mail_admins
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger(__name__)

class GhettoTimer(object):
    def __init__(self, orig_func):
        self.__name__ = 'GhettoTimer'
        self.orig_func = orig_func

    def __call__(self, *args, **kwargs):
        start_time = time.time()
        response = self.orig_func(*args, **kwargs)
        delta = time.time()-start_time
        holy_shit = '\n=!=!=!=!=!=!=!=!=!=!=!=!=!=!=!=!=!=!=!=!=!=!=!=\
                     !=!=!=!=!=!=!=!=!=!=!=!=!=!=!=!=!=!=!=!=!=!=!=!=!\n'
        msg = "Time to execute %s (%s): %s seconds" % (self.orig_func.__name__,
                                                       inspect.getsourcefile(self.orig_func),
                                                       round(delta, 4))
        if delta > 1:
            logger.critical('%s%s%s' % (holy_shit, msg, holy_shit))
            if cache.get('has_it_been_a_minute_yet') == None and settings.DEBUG == False:
                mail_admins('%s is slow as f*ck' % self.orig_func.__name__,
                        msg,
                        fail_silently=True)
                cache.set('has_it_been_a_minute_yet', True, 60)
        elif delta > 0.1:
            logger.warning('%s%s%s' % (holy_shit, msg, holy_shit))
        elif delta > 0.01:
            logger.info(msg)
        return response