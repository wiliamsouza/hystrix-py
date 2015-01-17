from __future__ import absolute_import
from collections import deque
from enum import Enum
import logging

log = logging.getLogger(__name__)


class RollingNumber(object):
    ''' A number which can be used to track counters (increment) or set values
        over time.

    It is "rolling" in the sense that a 'milliseconds' is given that you
    want to track (such as 10 seconds) and then that is broken into
    buckets (defaults to 10) so that the 10 second window doesn't empty
    out and restart every 10 seconds, but instead every 1 second you have
    a new bucket added and one dropped so that 9 of the buckets remain
    and only the newest starts from scratch.

    This is done so that the statistics are gathered over a rolling 10
    second window with data being added/dropped in 1 second intervals
    (or whatever granularity is defined by the arguments) rather than
    each 10 second window starting at 0 again.
    '''

    def __init__(self, time, milliseconds, bucket_numbers):
        self.time = time
        self.milliseconds = milliseconds
        self.buckets = BucketCircular(bucket_numbers)

        if self.milliseconds % bucket_numbers != 0:
            raise Exception('The milliseconds must divide equally into '
                            'bucket_numbers. For example 1000/10 is ok, '
                            '1000/11 is not.')

    def buckets_size_in_milliseconds(self):
        return self.milliseconds / self.buckets.maxlen

    def increment(self, event_type):
        pass


class BucketCircular(deque):
    ''' This is a circular array acting as a FIFO queue. '''

    def __init__(self, size):
        super(BucketCircular, self).__init__(maxlen=size + 1)
        self._buckets = []
        self.num_buckets = size
        self.state = []
        self.data_length = len(self._buckets)

    @property
    def size(self):
        return len(self.state)

    def get_last(self):
        return self.peek_last()

    def peek_last(self):
        return self.pop()


class RollingNumberEvent(Enum):
    ''' Various states/events that can be captured in the RollingNumber.

    Note that events are defined as different types:

    * Counter: is_counter() == true
    * MaxUpdater: is_max_updater() == true

    The Counter type events can be used with RollingNumber#increment,
    RollingNumber#add, RollingNumber#getRollingSum} and others.

    The MaxUpdater type events can be used with RollingNumber#updateRollingMax
    and RollingNumber#getRollingMaxValue.
    '''

    SUCCESS = 1
    FAILURE = 1
    TIMEOUT = 1
    SHORT_CIRCUITED = 1
    THREAD_POOL_REJECTED = 1
    SEMAPHORE_REJECTED = 1
    FALLBACK_SUCCESS = 1
    FALLBACK_FAILURE = 1
    FALLBACK_REJECTION = 1
    EXCEPTION_THROWN = 1
    THREAD_EXECUTION = 1
    THREAD_MAX_ACTIVE = 2
    COLLAPSED = 1
    RESPONSE_FROM_CACHE = 1

    def __init__(self, event_type):
        self.event_type = event_type

    def is_counter(self):
        return self.event_type == 1

    def is_max_updater(self):
        return self.event_type == 2
