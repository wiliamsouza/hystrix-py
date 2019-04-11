from __future__ import absolute_import
from enum import Enum
import logging


log = logging.getLogger(__name__)


class EventType(Enum):
    """ Various states/events that execution can result in or have tracked.

    These are most often accessed via :class:`hystrix.request_log.RequestLog`
    or :meth:`hystrix.command.Command.execution_events()`.
    """

    EMIT = 1
    SUCCESS = 2
    FAILURE = 3
    TIMEOUT = 4
    SHORT_CIRCUITED = 5
    THREAD_POOL_REJECTED = 6
    SEMAPHORE_REJECTED = 7
    FALLBACK_EMIT = 8
    FALLBACK_SUCCESS = 9
    FALLBACK_FAILURE = 10
    FALLBACK_REJECTION = 11
    EXCEPTION_THROWN = 12
    RESPONSE_FROM_CACHE = 13
    COLLAPSED = 14
    BAD_REQUEST = 15
