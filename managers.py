from django.db import models
from django.core.exceptions import ObjectDoesNotExist

class BetterManager(models.Manager):
    """
    This manager allows for one to do a lot of common things.
    It's intended to be a replacement for the default manager.
    """

    def get(self, **kwargs):
        if len(kwargs) > 1 and 'default' in kwargs:
            d = kwargs.pop('default')
            try:
                return super(BetterManager, self).get(**kwargs)
            except ObjectDoesNotExist:
                return d
        return super(BetterManager, self).get(**kwargs)
