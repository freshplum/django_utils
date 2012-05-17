from django.db import models
from django.core.exceptions import ObjectDoesNotExist


class QuerySetManager(models.Manager):
    # http://docs.djangoproject.com/en/dev/topics/db/managers/#using-managers-for-related-object-access
    # Not working cause of:
    # http://code.djangoproject.com/ticket/9643
    use_for_related_fields = True

    def __init__(self, qs_class=models.query.QuerySet):
        self.queryset_class = qs_class
        super(QuerySetManager, self).__init__()

    def get_query_set(self):
        return self.queryset_class(self.model)

    def __getattr__(self, attr, *args):
        try:
            return getattr(self.__class__, attr, *args)
        except AttributeError:
            return getattr(self.get_query_set(), attr, *args)


class QuerySet(models.query.QuerySet):
    """Base QuerySet class for adding custom methods that are made
    available on both the manager and subsequent cloned QuerySets"""

    @classmethod
    def as_manager(cls, ManagerClass=QuerySetManager):
        return ManagerClass(cls)



class BetterQuerySet(QuerySet):
    """
    This QuerySet set allows for one to do a lot of common things.
    It's intended to be a replacement for the default QuerySet manager.
    """

    def get(self, **kwargs):
        if len(kwargs) > 1 and 'default' in kwargs:
            d = kwargs.pop('default')
            try:
                #return None
                return super(BetterQuerySet, self).get(**kwargs)
            except ObjectDoesNotExist:
                return d
        return super(BetterQuerySet, self).get(**kwargs)