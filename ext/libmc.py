__author__ = 'jia'
import pylibmc


class PyLibMcNamespaceManager(object):
    def __init__(self, timeout, url, *arg):
        self.timeout = timeout
        self.mc = pylibmc.Client([url])
        self.pool = pylibmc.ThreadMappedPool(self.mc)

    def __getitem__(self, key):
        v = self.get(key)
        if v is None:
            raise KeyError()
        return v

    def __contains__(self, key):
        with self.pool.reserve() as mc:
            value = mc.get(key)
            return value is not None

    def has_key(self, key):
        return key in self

    def get(self, key):
        with self.pool.reserve() as mc:
            return mc.get(key)

    def set(self, key, value):
        with self.pool.reserve() as mc:
            if self.timeout:
                mc.set(key, value, self.timeout)
            else:
                mc.set(key, value)

    def __setitem__(self, key, value):
        self.set_value(key, value)

    def __delitem__(self, key):
        with self.pool.reserve() as mc:
            mc.delete(key)

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
            return mc.set_multi(kwargs.update(_dict), self.timeout)