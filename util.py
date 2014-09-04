__author__ = 'jia'
import warnings
import types


def verify_rules(params, ruleset):
    for key, types, message in ruleset:
        if key in params:
            params[key] = verify_options(params[key], types, message)
    return params



def coerce_cache_params(params):
    rules = [
        ('data_dir', (str, types.NoneType), "data_dir must be a string "
         "referring to a directory."),
        ('lock_dir', (str, types.NoneType), "lock_dir must be a string referring to a "
         "directory."),
        ('type', (str,), "Cache type must be a string."),
        ('enabled', (bool, types.NoneType), "enabled must be true/false "
         "if present."),
        ('expire', (int, types.NoneType), "expire must be an integer representing "
         "how many seconds the cache is valid for"),
        ('regions', (list, tuple, types.NoneType), "Regions must be a "
         "comma seperated list of valid regions"),
        ('key_length', (int, types.NoneType), "key_length must be an integer "
         "which indicates the longest a key can be before hashing"),
    ]
    return verify_rules(params, rules)


def format_cache_config_options(config, include_default):
    """

    """
    # warnings.warn("the old_format_cache_config_options func is deprecated; use format_cache_config_options instead",
    #             DeprecationWarning, 2)

    if include_default:
        options = dict(type='memory', data_dir=None, expire=None, log_file=None, enable=True)
    else:
        options = {}
    _options_mid = {}
    for key, value in config.iteritems():
        splits = key.split('.')
        assert 3 >= splits > 0
        _options_mid[splits] = value


    coerce_cache_params(options)