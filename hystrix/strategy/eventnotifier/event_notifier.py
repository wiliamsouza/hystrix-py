from __future__ import absolute_import
import logging

log = logging.getLogger(__name__)


class AbstractBaseEventNotifier(object):
    """ Abstract base EventNotifier that allows receiving notifications for
    different events with default implementations.

    See :class:`hystrix.strategy.plugins.Plugin` or the Hystrix GitHub Wiki
    for information on `configuring plugins
    <https://github.com/Netflix/Hystrix/wiki/Plugins>`_.

    .. note::
        Note on thread-safety and performance

        A single implementation of this class will be used globally so methods
        on this class will be invoked concurrently from multiple threads so
        all functionality must be thread-safe.

        Methods are also invoked synchronously and will add to execution time
        of the commands so all behavior should be fast. If anything
        time-consuming is to be done it should be spawned asynchronously
        onto separate worker threads.
    """

    def mark_event(self, event_type, command_name):
        """ Called for every event fired.

        This is the default Implementation and does nothing

        Args:
            event_type: A :class:hystrix.event_type.EventType` occurred
                during execution.
            command_key: Command instance name.
        """

        # Do nothing
        pass

    def mark_command_execution(self, command_name, isolation_strategy, duration, events_type):
        """ Called after a command is executed using thread isolation.

        Will not get called if a command is rejected, short-circuited etc.

        This is the default Implementation and does nothing

        Args:
            command_key: Command instance name.
            isolation_strategy: :class:`ExecutionIsolationStrategy` the
                isolation strategy used by the command when executed
            duration: Time in milliseconds of executing
                :meth:`hystrix.command.Command.run()` method.
            events_type: A list of :class:hystrix.event_type.EventType` of events
                occurred during execution.
        """

        # Do nothing
        pass
