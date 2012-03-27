from django.core.cache import cache
try:
    from plum.settings import ALLOW_CACHING
except ImportError:
    ALLOW_CACHING = True

try:
    from plum.settings import CACHE_TIMEOUT
except ImportError:
    CACHE_TIMEOUT = 5

class MemcachedClass(object):
    def __init__(self, ckey_uid=None):
        pass

    @property
    def ckey(self):
        key = self.__class__.__name__
        if hasattr(self, 'get_ckey_uid'):
            key += ('_%s' % self.get_ckey_uid)
        return key

class memcached_property(object):
    """
    Decorator that creates a property that caches its value in memcached
    """
    def __init__(self, fget=None, fset=None, fdel=None, name=None, doc=None, ckey='ckey', try_cache=True, dont_cache=False):
        self.fget = fget
        self.fset = fset
        self.fdel = fdel
        self.name = name
        self.__doc__ = doc
        self.ckey = ckey

        self.try_cache = try_cache
        self.dont_cache = dont_cache

    def __get__(self, obj, klass=None):
        if not self.try_cache or not ALLOW_CACHING or hasattr(obj, 'no_cache'):
            value = self.fget(obj)
        else:
            value = cache.get(self._ckey(obj))
            if value == None:
                value = self.fget(obj)
            else:
                pass
        self._save_to_cache(obj, value)
        return value

    def __set__(self, obj, value):
        raise AttributeError, "readonly property"

    def __delete__(self, obj):
        if self.fdel is None:
            cache.delete(obj._ckey)

    def _ckey(self, obj):
        if not hasattr(obj, self.ckey):
            raise AttributeError, 'cache key method does not exist. Tried to find method: '
        ckey = getattr(obj, self.ckey)
        return '%s_%s' % (ckey, self.fget.__name__)

    def _save_to_cache(self, obj, value):
        if not self.dont_cache and ALLOW_CACHING and not hasattr(obj, 'no_cache'):
            return cache.set(self._ckey(obj), value)
        return False



