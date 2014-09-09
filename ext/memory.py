__author__ = 'Leo'
import datetime


class MemoryNamespaceManager(object):

    def __init__(self, timeout):
        self.timeout = timeout
        self.data = {}
        self.overtime = {}

    def __getitem__(self, key):
        vt = self.data[key]
        if self.overtime.get[key] > datetime.datetime.now():
            self.__delitem__(key)
            raise KeyError(key)
        return vt

    def __contains__(self, key):
        return self.data.__contains__(key)

    def __delitem__(self, key):
        del self.data[key]
        del self.overtime[key]

    def has_key(self, key):
        return key in self

    def get(self, key):
        vt = self.data.get(key)
        if vt and self.overtime.get(key) > datetime.datetime.now():
            self.__delitem__(key)
            return None
        return vt

    def __setitem__(self, key, value):
        overtime = datetime.datetime.now() + datetime.timedelta(seconds=self.timeout)
        self.overtime[key] = overtime
        return self.data.__setitem__(key, value)

    def set(self, key, value):
        return self.__setitem__(key, value)

    def do_remove(self):
        self.data = {}

    def get_multi(self, keys):
        rst = []
        _now = datetime.datetime.now()
        for k in keys:
            v = self.data.get(k)
            if v is None:
                rst.append(None)
            elif self.overtime[k] > _now:
                rst.append(None)
                self.__delitem__(k)
            else:
                rst.append(v)
        return rst

    def set_multi(self, _dict, **kwargs):
        """
        :param _dict: a dict object which has __str__ function element
        :param kwargs: It has __str__ function object or base type
        :return: a null list
        """
        overtime = datetime.datetime.now() + datetime.timedelta(seconds=self.timeout)
        kwargs.update(_dict)
        self.overtime.update({k: overtime for k in kwargs.keys()})
        self.data.update(kwargs)
        return 1