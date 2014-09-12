# coding=utf-8
__author__ = 'Leo'

if __name__ == '__main__':
    import sys
    import os
    sys.path.append(os.path.realpath('.'))


class MonConfigError(Exception):
    def __init__(self, *args):
        super(Exception, self).__init__(*args)


class Message(object):
    """
    how to get element:
    if you want to get same level other attr:
    m = Message(...)
    m[-1]['pid']
    if you don't know where is the 'pid' :
    m.get_attr('pid'),
    """
    def __init__(self, dd, full_key, rule, *args):
        assert isinstance(dd, dict)
        self.full_key = full_key
        self.rule = rule
        self.source = dd
        self.key_list = list(args)
        self.__init_value_list()

    def __init_value_list(self):
        search_list = self.key_list
        self.value_list = [self.source]
        for index in xrange(len(search_list)):
            v = search_list[index]
            try:
                d = self.value_list[-1][v]
                self.value_list.append(d)
            except KeyError, what:
                raise MonConfigError(
                    '%s has invalid key:<%s>%s' % (str(self), index, v)
                )
            except IndexError, what:
                raise MonConfigError(
                    '%s has out of range index:<%s>%s' % (str(self), index, v)
                )
            except TypeError, what:
                raise MonConfigError(
                    '%s has type error:<%s>%s%s' % (str(self), index, v, type(self.value_list[-1]))
                )
            except Exception, what:
                raise MonConfigError(
                    '%s has unknow error:<%s>%s' % (str(self), index, v)
                )

    def deep(self, *args):
        self.key_list.extend(args)

    def last(self):
        return self[-1]

    def data(self):
        return self[len(self.key_list)]

    def deep_and_cpoy(self, *args):
        return self.__class__(self.source, self.full_key, self.rule, *(self.key_list + list(args)))

    def key(self, index):
        return self.key_list[index]

    def __getitem__(self, item):
        return self.value_list[item]

    def get_attr(self, key, top_level=0):
        assert isinstance(key, basestring)
        for i in xrange(len(self.key_list) - 1, top_level - 1, -1):
            if isinstance(self[i], (list, tuple)):
                continue
            elif isinstance(self[i], dict):
                ele = self[i].get(key)
                if not ele is None:
                    return ele
            else:
                continue
        return None

    def real_key(self):
        return '.'.join(str(i) for i in self.key_list)

    def __str__(self):
        return '{%s: %s}' % (self.full_key, self.rule) + self.real_key()

    __repr__ = __str__

    def __len__(self):
        return len(self.key_list)

#=====================================================
#            private func
#=====================================================


def check_targets_rule(rule, dd):
    """
    :param rule: just like: {'a.*.b':20} or {'a.d.c':[20,40]}
    :param dd: data dict
    :return: a dict with out of range data
    """
    assert isinstance(rule, dict)
    assert isinstance(dd, dict)
    error = []
    for k, r in rule.iteritems():
        error += _check_targets_rule(k, r, dd)
    return error


def _check_targets_rule(full_key, rule, dd):
    bind_value = _rule_bind(full_key, rule, dd)
    check_func = _create_check(rule)
    error_value = [bv for bv in bind_value if not check_func(bv.data())]
    return error_value


def _rule_bind(full_key, rule, dd):
    k_list = full_key.split('.')
    bind_value_list = [Message(dd, full_key, rule)]
    for _k in k_list:
        _bind_value_list = []
        if _k == '*':
            for bv in bind_value_list:
                if isinstance(bv.data(), (list, tuple)):
                    for _n in xrange(len(bv.data())):
                        _sbv = bv.deep_and_cpoy(_n)
                        _bind_value_list.append(_sbv)
                elif isinstance(bv.data(), dict):
                    for k in bv.data().keys():
                        _sbv = bv.deep_and_cpoy(k)
                        _bind_value_list.append(_sbv)
                else:
                    #  TODO construct is so bad
                    raise MonConfigError(
                        '%s.%s has error key:<%s>%s' % (str(bv), _k, len(bv), _k))

        else:
            for bv in bind_value_list:
                if isinstance(bv.data(), (list, tuple)):
                    try:
                        _k = int(_k)
                    except ValueError, what:
                        #  TODO construct is so bad
                        raise MonConfigError(
                            '%s.%s has error key:<%s>%s' % (str(bv), _k, len(bv), _k))
                _sbv = bv.deep_and_cpoy(_k)
                _bind_value_list.append(_sbv)


        bind_value_list = _bind_value_list
    return bind_value_list


def _create_check(rule):
    if isinstance(rule, dict):
        def _dict_check(value):
            if '$max' in rule and value > rule['$max']:
                return False
            if '$min' in rule and value < rule['$min']:
                return False
            if '$type' in rule and type(value) != rule['$type']:
                return False
            if '$in' in rule and value not in rule['$in']:
                return False
            return True
        return _dict_check
    else:
        def _simple_check(value):
            return rule == value
        return _simple_check

#a={u'load': 0, u'uid': 496, u'pid': 22512, u'locks': [{u'user 0': 0}, {u'signal': 0}, {u'filemon': 0}, {u'timer': 0}, {u'rbtimer': 0}, {u'cron': 0}, {u'thunder': 22515}, {u'rpc': 0}, {u'snmp': 0}], u'signal_queue': 0, u'sockets': [{u'can_offload': 0, u'name': u':8081', u'proto': u'http', u'queue': 0, u'shared': 0, u'max_queue': 100}, {u'can_offload': 0, u'name': u':8082', u'proto': u'uwsgi', u'queue': 0, u'shared': 0, u'max_queue': 100}], u'workers': [{u'status': u'idle', u'respawn_count': 1, u'tx': 3142, u'delta_requests': 16, u'last_spawn': 1409034434, u'apps': [{u'modifier1': 0, u'chdir': u'', u'startup_time': 0, u'exceptions': 0, u'mountpoint': u'', u'requests': 16, u'id': 0}], u'harakiri_count': 0, u'signals': 0, u'exceptions': 0, u'accepting': 1, u'id': 1, u'avg_rt': 8396, u'signal_queue': 0, u'cores': [{u'in_request': 0, u'vars': [], u'write_errors': 0, u'static_requests': 0, u'routed_requests': 0, u'requests': 16, u'offloaded_requests': 0, u'read_errors': 0, u'id': 0}], u'requests': 16, u'rss': 0, u'vsz': 0, u'pid': 22513, u'running_time': 216444}, {u'status': u'idle', u'respawn_count': 1, u'tx': 8138, u'delta_requests': 16, u'last_spawn': 1409034434, u'apps': [{u'modifier1': 0, u'chdir': u'', u'startup_time': 0, u'exceptions': 0, u'mountpoint': u'', u'requests': 16, u'id': 0}], u'harakiri_count': 0, u'signals': 0, u'exceptions': 0, u'accepting': 1, u'id': 2, u'avg_rt': 9252, u'signal_queue': 0, u'cores': [{u'in_request': 0, u'vars': [], u'write_errors': 0, u'static_requests': 0, u'routed_requests': 0, u'requests': 16, u'offloaded_requests': 0, u'read_errors': 0, u'id': 0}], u'requests': 16, u'rss': 0, u'vsz': 0, u'pid': 22514, u'running_time': 221493}, {u'status': u'idle', u'respawn_count': 1, u'tx': 2843, u'delta_requests': 15, u'last_spawn': 1409034434, u'apps': [{u'modifier1': 0, u'chdir': u'', u'startup_time': 0, u'exceptions': 0, u'mountpoint': u'', u'requests': 15, u'id': 0}], u'harakiri_count': 0, u'signals': 0, u'exceptions': 0, u'accepting': 1, u'id': 3, u'avg_rt': 7564, u'signal_queue': 0, u'cores': [{u'in_request': 0, u'vars': [], u'write_errors': 0, u'static_requests': 0, u'routed_requests': 0, u'requests': 15, u'offloaded_requests': 0, u'read_errors': 0, u'id': 0}], u'requests': 15, u'rss': 0, u'vsz': 0, u'pid': 22515, u'running_time': 183440}, {u'status': u'idle', u'respawn_count': 1, u'tx': 2325, u'delta_requests': 16, u'last_spawn': 1409034434, u'apps': [{u'modifier1': 0, u'chdir': u'', u'startup_time': 0, u'exceptions': 0, u'mountpoint': u'', u'requests': 16, u'id': 0}], u'harakiri_count': 0, u'signals': 0, u'exceptions': 0, u'accepting': 1, u'id': 4, u'avg_rt': 7440, u'signal_queue': 0, u'cores': [{u'in_request': 0, u'vars': [], u'write_errors': 0, u'static_requests': 0, u'routed_requests': 0, u'requests': 16, u'offloaded_requests': 0, u'read_errors': 0, u'id': 0}], u'requests': 16, u'rss': 0, u'vsz': 0, u'pid': 22516, u'running_time': 188050}], u'listen_queue': 0, u'listen_queue_errors': 0, u'version': u'2.0.4', u'gid': 496, u'cwd': u'/opt/advert/source'}
#
#messages = monitor_targets_rule({'locks.*.user 0':11,'uid':{'max':300},'workers.*.apps.*.modifier1':{'min':-1,'max':1},'workers.*.avg_rt':{'min':0,'max':9000}}, a)
#
#for m in messages:
#    print m.get_attr('pid'), m.data()
#    print m.get_detail()
