__author__ = 'jia'
import pylibmc
import hashlib
MAX_KEY_LENGTH = 250


class PyLibMcNamespaceManager(object):
    def __init__(self, *arg, **kw):
        self.mc = pylibmc.Client(*arg, **kw)
        self.pool = pylibmc.ThreadMappedPool(self.mc)

    def _format_key(self, key):
        if not isinstance(key, str):
            key = key.decode('ascii')
        formated_key = (self.namespace + '_' + key).replace(' ', '\302\267')
        if len(formated_key) > MAX_KEY_LENGTH:
            formated_key = hashlib.sha1(formated_key).hexdigest()
        return formated_key

    def __getitem__(self, key):
        with self.pool.reserve() as mc:
            return mc.get(self._format_key(key))

    def __contains__(self, key):
        with self.pool.reserve() as mc:
            value = mc.get(self._format_key(key))
            return value is not None

    def has_key(self, key):
        return key in self

    def set_value(self, key, value, expiretime=None):
        with self.pool.reserve() as mc:
            if expiretime:
                mc.set(self._format_key(key), value, time=expiretime)
            else:
                mc.set(self._format_key(key), value)

    def __setitem__(self, key, value):
        self.set_value(key, value)

    def __delitem__(self, key):
        with self.pool.reserve() as mc:
            mc.delete(self._format_key(key))

    def do_remove(self):
        with self.pool.reserve() as mc:
            mc.flush_all()

    def get_multi(self, keys):
        with self.pool.reserve() as mc:
            value_dict = mc.get_multi(keys)
            return [value_dict.get(k) for k in keys]

    def set_multi(self, _dict, **kwargs):
        """
        :param _dict: a dict object which has __str__ function element
        :param kwargs: It has __str__ function object or base type
        :return: a null list
        """
        with self.pool.reserve() as mc:
            return mc.set(kwargs.update(_dict))