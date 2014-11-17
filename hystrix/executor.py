from __future__ import absolute_import, unicode_literals
from concurrent.futures import ThreadPoolExecutor
import logging

import six

log = logging.getLogger(__name__)

MAX_WORKERS = 5


class ExecutorMetaclass(type):

    __executors = dict()
    __blacklist = ('Executor', 'ExecutorMetaclass')

    def __new__(cls, name, bases, attrs):

        if name in cls.__blacklist:
            return super(ExecutorMetaclass, cls).__new__(cls, name,
                                                         bases, attrs)

        classname = attrs.get('__executorname__', '{}Executor'.format(name))
        new_class = super(ExecutorMetaclass, cls).__new__(cls, classname,
                                                          bases, attrs)
        if classname not in cls.__executors:
            setattr(new_class, 'executor_name', classname)
            cls.__executors[classname] = new_class

        return cls.__executors[classname]


class Executor(six.with_metaclass(ExecutorMetaclass, ThreadPoolExecutor)):

    __executorname__ = None

    def __init__(self, max_workers=MAX_WORKERS):
        super(Executor, self).__init__(max_workers)
