__author__ = 'jia'
import warnings
import types
from string import replace
import hashlib
import sys
import os

default_hash = hashlib.sha1
default_hash_len = len(default_hash().hexdigest())


class CompressionInt(object):
    use_symbol = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

    def __init__(self, symbols=use_symbol):
        assert not '-' in symbols
        self.use_symbol = symbols
        self.symbol_len = len(self.use_symbol)

    def __call__(self, num):
        rst = ""
        if num < 0:
            num = abs(num)
            rst = '-'
        while num:
            re = num % self.symbol_len
            rst += self.use_symbol[re]
            num /= self.symbol_len
        return rst

    def reverse(self, data):
        num = 0
        if data and data[0] == '-':
            data = data[:0:-1]
            pn = -1
        else:
            data = data[::-1]
            pn = 1
        for s in data:
            f = self.use_symbol.find(s)
            if f != -1:
                num = num * self.symbol_len + f
        return num * pn


def __get_cache(namespace, key_args, max_key_length):
    format_key = str(key_args)
    format_key_length = len(format_key)
    namespace_length = len(namespace)
    if format_key_length + namespace_length > max_key_length:
        if namespace_length + default_hash_len > max_key_length:
            return default_hash(str(namespace) + format_key)
        return namespace + default_hash(format_key)
    return namespace + format_key


def get_cache(namespace, key_args, max_key_length=256):
    return __get_cache(namespace, key_args, max_key_length).replace(' ', '_')


def is_global(obj):
    mod = obj.__module__
    __import__(mod)
    module = sys.modules(mod)
    return hasattr(module, obj.__name__)


def get_module_name(module):
    return os.path.realpath(module)


def get_func_name(func):
    if is_global(func):
        return func.__name__
    else:
        return CompressionInt(hash(func.func_code.co_code))


def im_func_name(func):
    im_class = func.im_class
    if is_global(im_class):
        return '%s.%s' % (im_class.__name__, func.__name__)
    else:
        #so hard
        assert 0


def create_namespace(func):
    module = func.__module__
    module_name = get_module_name(module)
    if isinstance(func, types.MethodType):
        func_name = im_func_name(func)
    else:
        func_name = get_func_name(func)
    return '%s|%s' % (module, func_name)


try:
    import threading

except Exception, what:
    print 'Warning: import threading model failure'

    def async(func, *args, **kwargs):
        func(*args, **kwargs)

else:
    def async(func, *args, **kwargs):
        t = threading.Thread(target=func, args=args, kwargs=kwargs)
        t.setDaemon(True)
        t.start()