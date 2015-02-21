from __future__ import absolute_import
import logging

import six

from hystrix.metrics import Metrics
from hystrix.rolling_number import RollingNumber

log = logging.getLogger(__name__)


class CommandMetricsMetaclass(type):
    """ Metaclass for :class:`CommandMetrics`

    Return a cached or create the :class:`CommandMetrics` instance for a given
    :class:`hystrix.command.Command` name.

    This ensures only 1 :class:`CommandMetrics` instance per
    :class:`hystrix.command.Command` name.
    """

    __instances__ = dict()
    __blacklist__ = ('CommandMetrics', 'CommandMetricsMetaclass')

    def __new__(cls, name, bases, attrs):

        # Do not use cache for black listed classes.
        if name in cls.__blacklist__:
            return super(CommandMetricsMetaclass, cls).__new__(cls, name,
                                                               bases, attrs)

        # User defined class name or create a default.
        class_name = attrs.get('__command_metrics_name__',
                               '{}CommandMetrics'.format(name))

        # Check for CommandMetrics class instance
        if class_name not in cls.__instances__:
            new_class = super(CommandMetricsMetaclass, cls).__new__(cls,
                                                                    class_name,
                                                                    bases,
                                                                    attrs)
            setattr(new_class, 'command_metrics_name', class_name)
            cls.__instances__[class_name] = new_class

        return cls.__instances__[class_name]


class CommandMetrics(six.with_metaclass(CommandMetricsMetaclass, Metrics)):
    """ Used by :class:`hystrix.command.Command` to record metrics.
    """
    __command_metrics_name__ = None

    def __init__(self, command_name, command_group, properties, event_notifier):
        counter = RollingNumber(properties.metrics_rolling_statistical_window_in_milliseconds(),
                                properties.metrics_rolling_statistical_window_buckets())
        super(CommandMetrics, self).__init__(counter)


class HealthCounts(object):
    """ Number of requests during rolling window.

    Number that failed (failure + success + timeout + thread pool rejected +
    short circuited + semaphore rejected).

    Error percentage;
    """
    def __init__(self, total, error, error_percentage):
        self._total_count = total
        self._error_count = error
        self._error_percentage = error_percentage

    def total_requests(self):
        """ Total reqeust

        Returns:
            int: Returns total request count.
        """
        return self._total_count

    def error_count(self):
        """ Error count

        Returns:
            int: Returns error count.
        """
        return self._error_count

    def error_percentage(self):
        """ Error percentage

        Returns:
            int: Returns error percentage.
        """
        return self._error_percentage
