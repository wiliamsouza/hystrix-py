from __future__ import absolute_import
from concurrent.futures import ThreadPoolExecutor
import logging

import six

log = logging.getLogger(__name__)

MAX_WORKERS = 5


class ExecutorMetaclass(type):

    __instances__ = dict()
    __blacklist__ = ('Executor', 'ExecutorMetaclass')

    def __new__(cls, name, bases, attrs):

        if name in cls.__blacklist__:
            return super(ExecutorMetaclass, cls).__new__(cls, name,
                                                         bases, attrs)

        class_name = attrs.get('__executor_name__', '{}Executor'.format(name))
        new_class = super(ExecutorMetaclass, cls).__new__(cls, class_name,
                                                          bases, attrs)
        if class_name not in cls.__instances__:
            setattr(new_class, 'executor_name', class_name)
            cls.__instances__[class_name] = new_class

        return cls.__instances__[class_name]


class Executor(six.with_metaclass(ExecutorMetaclass, ThreadPoolExecutor)):

    __executor_name__ = None

    def __init__(self, max_workers=MAX_WORKERS):
        super(Executor, self).__init__(max_workers)
