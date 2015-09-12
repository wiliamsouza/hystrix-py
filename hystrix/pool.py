from __future__ import absolute_import
from concurrent.futures import ThreadPoolExecutor
import logging

import six

log = logging.getLogger(__name__)


class PoolMetaclass(type):

    __instances__ = dict()
    __blacklist__ = ('Pool', 'PoolMetaclass')

    def __new__(cls, name, bases, attrs):

        if name in cls.__blacklist__:
            return super(PoolMetaclass, cls).__new__(cls, name,
                                                     bases, attrs)

        pool_key = attrs.get('pool_key') or '{}Pool'.format(name)
        new_class = super(PoolMetaclass, cls).__new__(cls, pool_key,
                                                      bases, attrs)

        setattr(new_class, 'pool_key', pool_key)

        if pool_key not in cls.__instances__:
            cls.__instances__[pool_key] = new_class

        return cls.__instances__[pool_key]


class Pool(six.with_metaclass(PoolMetaclass, ThreadPoolExecutor)):

    pool_key = None

    def __init__(self, pool_key=None, max_workers=5):
        super(Pool, self).__init__(max_workers)
