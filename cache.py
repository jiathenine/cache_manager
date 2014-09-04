__author__ = 'jia'

region_config = {}

def cache_region(region, manager, *region_args):
    def decorator(func):
        def _decorator(*args, **kwargs):
            