from __future__ import absolute_import
import logging

log = logging.getLogger(__name__)


# TODO: Rename this to AbstractMetrics
class Metrics(object):
    """ Base class for metrics

    Args:
        counter (:class:`hystrix.rolling_number.RollingNumber`): Used to
            increment or set values over time.
    """

    def __init__(self, counter):
        self.counter = counter

    def cumulative_count(self, event):
        """ Cumulative count

        Get the **cumulative** count since the start of the application for the
        given :class:`RollingNumberEvent`.

        Args:
            event (:class:`RollingNumberEvent`): The Event to retrieve a
                **sum** for.

        Returns:
            long: Returns the long cumulative count.
        """
        return self.counter.cumulative_sum(event)

    def rolling_count(self, event):
        """ **Rolling** count

        Get the rolling count for the given:class:`RollingNumberEvent`.

        Args:
            event (:class:`RollingNumberEvent`): The Event to retrieve a
                **sum** for.

        Returns:
            long: Returns the long cumulative count.
        """
        return self.counter.rolling_sum(event)
