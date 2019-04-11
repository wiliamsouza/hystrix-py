from __future__ import absolute_import
import logging

import six

log = logging.getLogger(__name__)


class PoolMetricsMetaclass(type):

    __instances__ = dict()
    __blacklist = ('PoolMetrics', 'PoolMetricsMetaclass')

    def __new__(cls, name, bases, attrs):

        if name in cls.__blacklist:
            return super(PoolMetricsMetaclass, cls).__new__(cls, name,
                                                            bases, attrs)

        pool_metrics_key = attrs.get('pool_metrics_key') or \
            '{}PoolMetrics'.format(name)

        new_class = super(PoolMetricsMetaclass, cls).__new__(cls,
                                                             pool_metrics_key,
                                                             bases, attrs)
        setattr(new_class, 'pool_metrics_key', pool_metrics_key)

        if pool_metrics_key not in cls.__instances__:
            cls.__instances__[pool_metrics_key] = new_class

        return cls.__instances__[pool_metrics_key]


class PoolMetrics(six.with_metaclass(PoolMetricsMetaclass, object)):

    pool_metrics_key = None
