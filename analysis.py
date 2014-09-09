__author__ = 'jia'
import types
import re


def coerce_cache_params(params):
    rules = {
        '*.type': {'$in': ('memory', 'memcached', 'pylibmc')},
        '*.key': {'type': basestring},
        '*.expire': {'type': int},
        '*.url': {'type': basestring},
    }
    # return verify_rules(params, rules)


def format_cache_config_options(config):
    """

    """
    # warnings.warn("the old_format_cache_config_options func is deprecated; use format_cache_config_options instead",
    #             DeprecationWarning, 2)
    _options_mid = {}
    for key, value in config.iteritems():
        splits = key.split('.', 2)
        assert len(splits) == 3
        region = splits[1]
        attr = splits[2]
        if not _options_mid.has_key(region):
            _options_mid[region] = {}
        _options_mid[region][attr] = value


    coerce_cache_params(_options_mid)