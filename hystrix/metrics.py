from __future__ import absolute_import
import logging

import six

log = logging.getLogger(__name__)

MAX_WORKERS = 5


class CommandMetricsMetaclass(type):

    __instances__ = dict()
    __blacklist__ = ('CommandMetrics', 'CommandMetricsMetaclass')

    def __new__(cls, name, bases, attrs):

        if name in cls.__blacklist__:
            return super(CommandMetricsMetaclass, cls).__new__(cls, name,
                                                               bases, attrs)

        classname = attrs.get('__command_metrics_name__',
                              '{}CommandMetrics'.format(name))
        new_class = super(CommandMetricsMetaclass, cls).__new__(cls, classname,
                                                                bases, attrs)
        setattr(new_class, 'command_metrics_name', classname)

        if classname not in cls.__instances__:
            cls.__instances__[classname] = new_class

        return cls.__instances__[classname]


class CommandMetrics(six.with_metaclass(CommandMetricsMetaclass, object)):

    __command_metrics_name__ = None


class ExecutorMetricsMetaclass(type):

    __instances__ = dict()
    __blacklist = ('ExecutorMetrics', 'ExecutorMetricsMetaclass')

    def __new__(cls, name, bases, attrs):

        if name in cls.__blacklist:
            return super(ExecutorMetricsMetaclass, cls).__new__(cls, name,
                                                                bases, attrs)

        classname = attrs.get('__executor_metrics_name__',
                              '{}ExecutorMetrics'.format(name))
        new_class = super(ExecutorMetricsMetaclass, cls).__new__(cls,
                                                                 classname,
                                                                 bases, attrs)
        setattr(new_class, 'executor_metrics_name', classname)

        if classname not in cls.__instances__:
            cls.__instances__[classname] = new_class

        return cls.__instances__[classname]


class ExecutorMetrics(six.with_metaclass(ExecutorMetricsMetaclass, object)):

    __executor_metrics_name__ = None
