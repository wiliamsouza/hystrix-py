from __future__ import absolute_import, unicode_literals
import logging

import six

log = logging.getLogger(__name__)

MAX_WORKERS = 5


class CommandMetricsMetaclass(type):

    __commandmetricss = dict()
    __blacklist = ('CommandMetrics', 'CommandMetricsMetaclass')

    def __new__(cls, name, bases, attrs):

        if name in cls.__blacklist:
            return super(CommandMetricsMetaclass, cls).__new__(cls, name,
                                                               bases, attrs)

        classname = attrs.get('__commandmetricsname__', '{}CommandMetrics'.format(name))
        new_class = super(CommandMetricsMetaclass, cls).__new__(cls, classname,
                                                                bases, attrs)
        if classname not in cls.__commandmetricss:
            setattr(new_class, 'commandmetrics_name', classname)
            cls.__commandmetricss[classname] = new_class

        return cls.__commandmetricss[classname]


class CommandMetrics(six.with_metaclass(CommandMetricsMetaclass, object)):

    __commandmetricsname__ = None

    def __init__(self, max_workers=MAX_WORKERS):
        super(CommandMetrics, self).__init__(max_workers)


class ExecutorMetricsMetaclass(type):

    __executormetricss = dict()
    __blacklist = ('ExecutorMetrics', 'ExecutorMetricsMetaclass')

    def __new__(cls, name, bases, attrs):

        if name in cls.__blacklist:
            return super(ExecutorMetricsMetaclass, cls).__new__(cls, name,
                                                                bases, attrs)

        classname = attrs.get('__executormetricsname__', '{}ExecutorMetrics'.format(name))
        new_class = super(ExecutorMetricsMetaclass, cls).__new__(cls, classname,
                                                                 bases, attrs)
        if classname not in cls.__executormetricss:
            setattr(new_class, 'executormetrics_name', classname)
            cls.__executormetricss[classname] = new_class

        return cls.__executormetricss[classname]


class ExecutorMetrics(six.with_metaclass(ExecutorMetricsMetaclass, object)):

    __executormetricsname__ = None

    def __init__(self, max_workers=MAX_WORKERS):
        super(ExecutorMetrics, self).__init__(max_workers)
