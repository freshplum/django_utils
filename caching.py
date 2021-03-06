from django.core.cache import cache
from django.template.defaultfilters import slugify
from django.db.models.signals import post_save, pre_delete
from django.db.models.query import QuerySet
from django.db import models

#Simple GET caching.  Cribbed from http://www.eflorenzano.com/blog/post/drop-dead-simple-django-caching/
#Count caching


def key_from_instance(instance):
    opts = instance._meta
    return '%s.%s:%s' % (opts.app_label, opts.module_name, instance.pk)

def post_save_cache(sender, instance, **kwargs):
    cache.set(key_from_instance(instance), instance)
    #Disconnect until we use SimpleCacheQuerySet
#post_save.connect(post_save_cache)

def pre_delete_uncache(sender, instance, **kwargs):
    cache.delete(key_from_instance(instance))
#Disconnect until we use SimpleCacheQuerySet
#pre_delete.connect(pre_delete_uncache)

class SimpleCacheQuerySet(QuerySet):
    def filter(self, *args, **kwargs):
        pk = None
        for val in ('pk', 'pk__exact', 'id', 'id__exact'):
            if val in kwargs:
                pk = kwargs[val]
                break
        if pk is not None:
            opts = self.model._meta
            key = '%s.%s:%s' % (opts.app_label, opts.module_name, pk)
            obj = cache.get(key)
            if obj == None:
                res = super(SimpleCacheQuerySet, self).filter(*args, **kwargs)
                cache.set(key, res)
                return res
            else:
                self._result_cache = [obj]
        return super(SimpleCacheQuerySet, self).filter(*args, **kwargs)

class SimpleCacheManager(models.Manager):
    def get_query_set(self):
        return SimpleCacheQuerySet(self.model)

class CountCacheQuerySet(QuerySet):
    def count(self):
        opts = self.model._meta
        key = slugify(unicode(self.query))
        cache_qs = cache.get(key)
        if cache_qs != None:
            return cache_qs
        if cache_qs == None:
            qs = super(CountCacheQuerySet, self).count()
            cache.set(key, qs)
            return qs

class CacheCountManager(models.Manager):
    def get_query_set(self):
        return CountCacheQuerySet(self.model)


def cached(cache_key='', timeout_seconds=1800):
    """Django cache decorator

    Example 1:
    class MenuItem(models.Model):
        @classmethod
        @cached('menu_root', 3600*24)
        def get_root(self):
            return MenuItem.objects.get(pk=1)

    Example 2:
    @cached(lambda u: 'user_privileges_%s' % u.username, 3600)
    def get_user_privileges(user):
        #...
    """
    def _cached(func):
        def do_cache(*args, **kws):
            if isinstance(cache_key, str):
                key = cache_key % locals()
            elif callable(cache_key):
                key = cache_key(*args, **kws)
            data = cache.get(key)
            if data: return data
            data = func(*args, **kws)
            cache.set(key, data, timeout_seconds)
            return data
        return do_cache
    return _cached
