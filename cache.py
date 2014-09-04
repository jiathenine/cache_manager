__author__ = 'jia'
import beaker.cache
import inspect
import types
region_config = {}


class CacheManager(object):
    pass


def is_mem_func(func):
    return hasattr(func, '__self__') or inspect.getargspec(func).get()


def cache_region(region, manager, skip_pos=0, *deco_args):
    def decorator(func):
        def _decorator(*args):
            cache_ = region_config[manager].get_dbmanager(region)
            key = ' '.join(map(str, deco_args + region[skip_pos:]))
