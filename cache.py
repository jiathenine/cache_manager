__author__ = 'jia'
import beaker.cache
import inspect
import types
from ext import libmc
import util

region_config = {}


max_key_length = 256


class CacheManager(object):
    region_map = {
        'memcached': libmc.PyLibMcNamespaceManager,
        'pylibmc': libmc.PyLibMcNamespaceManager,
    }

    def __init__(self):
        self.db = {}

    def get_dbmanager(self, region):
        if region not in self.db:
            if region not in self.region_map:
                raise KeyError('%s database is not found' % region)
            self.db[region] = self.region_map[region]()


def is_mem_func(func):
    return hasattr(func, '__self__')


def cache_region(region, manager, deco_args=[]):
    def decorator(func):
        skip_self = is_mem_func(func)
        namespace = util.create_namespace(func)

        def _decorator(*args):
            cache_ = region_config[manager].get_dbmanager(region)
            key_args = deco_args + args[skip_self:]
            real_key = util.get_cache(namespace, key_args)
            try:
                value = cache_[real_key]
            except KeyError:
                value = func(*args)
                util.async(cache_.set, real_key, value)
            return value
        return _decorator
    return decorator

