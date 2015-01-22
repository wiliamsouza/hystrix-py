from __future__ import absolute_import
from multiprocessing import Value, Lock
from collections import deque
import logging
import types
import time

import six

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

    def __init__(self, _time, milliseconds, bucket_numbers):
        self.time = _time
        self.milliseconds = milliseconds
        self.buckets = BucketCircular(bucket_numbers)
        self.bucket_numbers = bucket_numbers
        self.cumulative_sum = CumulativeSum()
        self._new_bucket_lock = Lock()

        if self.milliseconds % self.bucket_numbers != 0:
            raise Exception('The milliseconds must divide equally into '
                            'bucket_numbers. For example 1000/10 is ok, '
                            '1000/11 is not.')

    def buckets_size_in_milliseconds(self):
        return self.milliseconds / self.bucket_numbers

    def increment(self, event):
        self.current_bucket().adder(event).increment()

    def update_rolling_max(self, event, value):
        self.current_bucket().max_updater(event).update(value)

    def current_bucket(self):
        current_time = self.time.current_time_in_millis()
        current_bucket = self.buckets.peek_last()

        if current_bucket is not None and current_time < current_bucket.window_start + self.buckets_size_in_milliseconds():
            return current_bucket

        with self._new_bucket_lock:
            # If we didn't find the current bucket above, then we have to
            # create one.
            if self.buckets.peek_last() is None:
                new_bucket = Bucket(current_time)
                self.buckets.add_last(new_bucket)
                return new_bucket
            else:
                for i in range(self.bucket_numbers):
                    last_bucket = self.buckets.peek_last()
                    if current_time < last_bucket.window_start + self.buckets_size_in_milliseconds():
                        return last_bucket
                    elif current_time - (last_bucket.window_start + self.buckets_size_in_milliseconds()) > self.milliseconds:
                        self.reset()
                        return self.current_bucket()
                    else:
                        self.buckets.add_last(Bucket(last_bucket.window_start + self.buckets_size_in_milliseconds()))
                        self.cumulative_sum.add_bucket(last_bucket)

                return self.buckets.peek_last()

        # we didn't get the lock so just return the latest bucket while
        # another thread creates the next one
        current_bucket = self.buckets.peek_last()
        if current_bucket is not None:
            return current_bucket
        else:
            # The rare scenario where multiple threads raced to create the
            # very first bucket wait slightly and then use recursion while
            # the other thread finishes creating a bucket
            time.sleep(5)
            self.current_bucket()

    def reset(self):
        last_bucket = self.buckets.peek_last()
        if last_bucket:
            self.cumulative_sum.add_bucket(last_bucket)

        self.buckets.clear()

    def rolling_sum(self, event):
        last_bucket = self.current_bucket()
        if not last_bucket:
            return 0

        sum = 0
        for bucket in self.buckets:
            sum += bucket.adder(event).sum()
        return sum

    def rolling_max(self, event):
        values = self.get_values(event)
        if not values:
            return 0
        else:
            return values[len(values) - 1]

    # TODO: Rename to values
    def get_values(self, event):
        last_bucket = self.current_bucket()
        if not last_bucket:
            return 0

        values = []
        for bucket in self.buckets:
            if event.is_counter():
                values.append(bucket.adder(event).sum())
            if event.is_max_updater():
                values.append(bucket.max_updater(event).max())
        return values

    def value_of_latest_bucket(self, event):
        last_bucket = self.current_bucket()
        if not last_bucket:
            return 0

        return last_bucket.get(event)


class BucketCircular(deque):
    ''' This is a circular array acting as a FIFO queue. '''

    def __init__(self, size):
        super(BucketCircular, self).__init__(maxlen=size)

    @property
    def size(self):
        return len(self)

    def last(self):
        return self.peek_last()

    def peek_last(self):
        try:
            return self[0]
        except IndexError:
            return None

    def add_last(self, bucket):
        self.appendleft(bucket)


class Bucket(object):
    ''' Counters for a given 'bucket' of time. '''

    def __init__(self, start_time):
        self.window_start = start_time
        self._adder = {}
        self._max_updater = {}

        # TODO: Change this to use a metaclass
        for name, event in RollingNumberEvent.__members__.items():
            if event.is_counter():
                self._adder[event.name] = LongAdder()

        for name, event in RollingNumberEvent.__members__.items():
            if event.is_max_updater():
                self._max_updater[event.name] = LongMaxUpdater()

    def get(self, event):
        if event.is_counter():
            return self.adder(event).sum()

        if event.is_max_updater():
            return self.max_updater(event).max()

        raise Exception('Unknown type of event.')

    # TODO: Rename to add
    def adder(self, event):
        if event.is_counter():
            return self._adder[event.name]

        raise Exception('Type is not a LongAdder.')

    # TODO: Rename to update_max
    def max_updater(self, event):
        if event.is_max_updater():
            return self._max_updater[event.name]

        raise Exception('Type is not a LongMaxUpdater.')


class LongAdder(object):

    def __init__(self, min_value=0):
        self.count = Value('i', min_value)
        self.lock = Lock()

    def increment(self):
        with self.lock:
            self.count.value += 1

    def decrement(self):
        with self.lock:
            self.count.value -= 1

    def sum(self):
        with self.lock:
            return self.count.value

    def add(self, value):
        with self.lock:
            self.count.value += value


class LongMaxUpdater(object):

    def __init__(self, min_value=0):
        self.count = Value('i', min_value)
        self.lock = Lock()

    def max(self):
        with self.lock:
            return self.count.value

    def update(self, value):
        if value > self.max():
            with self.lock:
                self.count.value = value


class CumulativeSum(object):

    def __init__(self):
        self._adder = {}
        self._max_updater = {}

        # TODO: Change this to use a metaclass
        for name, event in RollingNumberEvent.__members__.items():
            if event.is_counter():
                self._adder[event.name] = LongAdder()

        for name, event in RollingNumberEvent.__members__.items():
            if event.is_max_updater():
                self._max_updater[event.name] = LongMaxUpdater()

    def add_bucket(self, bucket):
        for name, event in RollingNumberEvent.__members__.items():
            if event.is_counter():
                self.adder(event).add(bucket.adder(event).sum())

            if event.is_max_updater():
                self.max_updater(event).update(bucket.max_updater(event).max())

    def get(self, event):
        if event.is_counter():
            return self.adder(event).sum()

        if event.is_max_updater():
            return self.max_updater(event).max()

        raise Exception('Unknown type of event.')

    def adder(self, event):
        if event.is_counter():
            return self._adder[event.name]

        raise Exception('Unknown type of event.')

    def max_updater(self, event):
        if event.is_max_updater():
            return self._max_updater[event.name]

        raise Exception('Unknown type of event.')


def _is_function(obj):
    return isinstance(obj, types.FunctionType)


def _is_dunder(name):
    return (name[:2] == name[-2:] == '__' and
            name[2:3] != '_' and
            name[-3:-2] != '_' and
            len(name) > 4)


class Event(object):

    def __init__(self, name, value):
        self._name = name
        self._value = value

    def is_counter(self):
        return self._value == 1

    def is_max_updater(self):
        return self._value == 2

    @property
    def name(self):
        return self._name

    @property
    def value(self):
        return self._value


class EventMetaclass(type):

    def __new__(cls, name, bases, attrs):
        __members = {}

        for name, value in attrs.items():
            if not _is_dunder(name) and not _is_function(value):
                __members[name] = Event(name, value)

        for name, value in __members.items():
            attrs[name] = __members[name]

        new_class = super(EventMetaclass, cls).__new__(cls, name,
                                                       bases, attrs)

        setattr(new_class, '__members__', __members)

        return new_class


class RollingNumberEvent(six.with_metaclass(EventMetaclass, object)):
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

    def __init__(self, event):
        self._event = event

    def is_counter(self):
        return self._event.value == 1

    def is_max_updater(self):
        return self._event.value == 2
