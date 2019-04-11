from __future__ import absolute_import
import logging

from hystrix.strategy.eventnotifier.event_notifier import AbstractBaseEventNotifier

log = logging.getLogger(__name__)


class EventNotifierDefault(AbstractBaseEventNotifier):
    """
    Default implementations of :class:`AbstractBaseEventNotifier` that does nothing.
    """

    INSTANCE = None

    @classmethod
    def get_instance(klass):
        if not klass.INSTANCE:
            klass.INSTANCE = klass()
        return klass.INSTANCE
