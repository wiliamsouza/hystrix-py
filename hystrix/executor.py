from __future__ import absolute_import
from concurrent.futures import ThreadPoolExecutor
import logging

import six

log = logging.getLogger(__name__)

MAX_WORKERS = 5


class ExecutorMetaclass(type):

    __instances__ = dict()
    __blacklist = ('Executor', 'ExecutorMetaclass')

    def __new__(cls, name, bases, attrs):

        if name in cls.__blacklist:
            return super(ExecutorMetaclass, cls).__new__(cls, name,
                                                         bases, attrs)

        classname = attrs.get('__executor_name__', '{}Executor'.format(name))
        new_class = super(ExecutorMetaclass, cls).__new__(cls, classname,
                                                          bases, attrs)
        if classname not in cls.__instances__:
            setattr(new_class, 'executor_name', classname)
            cls.__instances__[classname] = new_class

        return cls.__instances__[classname]


class Executor(six.with_metaclass(ExecutorMetaclass, ThreadPoolExecutor)):

    __executor_name__ = None

    def __init__(self, max_workers=MAX_WORKERS):
        super(Executor, self).__init__(max_workers)
