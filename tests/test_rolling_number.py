from multiprocessing import Value, Lock

from hystrix.rolling_number import RollingNumber, RollingNumberEvent

import pytest


def test_create_buckets():
    time = MockedTime()
    counter = RollingNumber(time, 200, 10)

    # confirm the initial settings
    assert counter.milliseconds == 200
    assert counter.bucket_numbers == 10
    assert counter.buckets_size_in_milliseconds() == 20

    # We start out with 0 buckets in the queue
    assert counter.buckets.size == 0

    # add a success in each interval which should result in all 10 buckets
    # being created with 1 success in each
    for r in range(counter.bucket_numbers):
        counter.increment(RollingNumberEvent.SUCCESS)
        time.increment(counter.buckets_size_in_milliseconds())

    # confirm we have all 10 buckets
    assert counter.buckets.size == 10

    # add 1 more and we should still only have 10 buckets since that's the max
    counter.increment(RollingNumberEvent.SUCCESS)
    assert counter.buckets.size == 10


def test_reset_buckets():
    time = MockedTime()
    counter = RollingNumber(time, 200, 10)

    # We start out with 0 buckets in the queue
    assert counter.buckets.size == 0

    # Add 1
    counter.increment(RollingNumberEvent.SUCCESS)

    # Confirm we have 1 bucket
    assert counter.buckets.size == 1

    # Confirm we still have 1 bucket
    assert counter.buckets.size == 1

    # Add 1
    counter.increment(RollingNumberEvent.SUCCESS)

    # We should now have a single bucket with no values in it instead of 2 or
    # more buckets
    assert counter.buckets.size == 1


def test_empty_buckets_fill_in():
    time = MockedTime()
    counter = RollingNumber(time, 200, 10)

    # We start out with 0 buckets in the queue
    assert counter.buckets.size == 0

    # Add 1
    counter.increment(RollingNumberEvent.SUCCESS)

    # Confirm we have 1 bucket
    assert counter.buckets.size == 1

    # Wait past 3 bucket time periods (the 1st bucket then 2 empty ones)
    time.increment(counter.buckets_size_in_milliseconds() * 3)

    # Add another
    counter.increment(RollingNumberEvent.SUCCESS)

    # We should have 4 (1 + 2 empty + 1 new one) buckets
    assert counter.buckets.size == 4


def test_increment_in_single_bucket():
    time = MockedTime()
    counter = RollingNumber(time, 200, 10)

    # We start out with 0 buckets in the queue
    assert counter.buckets.size == 0

    # Increment
    counter.increment(RollingNumberEvent.SUCCESS)
    counter.increment(RollingNumberEvent.SUCCESS)
    counter.increment(RollingNumberEvent.SUCCESS)
    counter.increment(RollingNumberEvent.SUCCESS)
    counter.increment(RollingNumberEvent.FAILURE)
    counter.increment(RollingNumberEvent.FAILURE)
    counter.increment(RollingNumberEvent.TIMEOUT)

    # Confirm we have 1 bucket
    assert counter.buckets.size == 1

    # The count should match
    assert counter.buckets.last().adder(RollingNumberEvent.SUCCESS).sum() == 4
    assert counter.buckets.last().adder(RollingNumberEvent.FAILURE).sum() == 2
    assert counter.buckets.last().adder(RollingNumberEvent.TIMEOUT).sum() == 1


def test_timeout():
    time = MockedTime()
    counter = RollingNumber(time, 200, 10)

    # We start out with 0 buckets in the queue
    assert counter.buckets.size == 0

    # Increment
    counter.increment(RollingNumberEvent.TIMEOUT)

    # We shoud have 1 bucket
    assert counter.buckets.size == 1

    # The count should match
    assert counter.buckets.last().adder(RollingNumberEvent.TIMEOUT).sum() == 1
    #import ipdb; ipdb.set_trace()  # Breakpoint
    assert counter.rolling_sum(RollingNumberEvent.TIMEOUT) == 1

    # Sleep to get to a new bucket
    time.increment(counter.buckets_size_in_milliseconds() * 3)

    # Incremenet again in latest bucket
    counter.increment(RollingNumberEvent.TIMEOUT)

    # We should have 4 buckets
    assert counter.buckets.size == 4

    # The count of the last bucket
    assert counter.buckets.last().adder(RollingNumberEvent.TIMEOUT).sum() == 1

    # The total count
    assert counter.rolling_sum(RollingNumberEvent.TIMEOUT) == 2


def test_milliseconds_buckets_size_error():
    time = MockedTime()

    with pytest.raises(Exception):
        RollingNumber(time, 100, 11)


def test_rolling_number_event_is_counter():
    event = RollingNumberEvent(RollingNumberEvent.SUCCESS)
    assert event.is_counter() is True


def test_rolling_number_event_is_max_updater():
    event = RollingNumberEvent(RollingNumberEvent.THREAD_MAX_ACTIVE)
    assert event.is_max_updater() is True


class MockedTime():

    def __init__(self):
        self._time = Value('f', 0)
        self._lock = Lock()

    def current_time_in_millis(self):
        with self._lock:
            return self._time.value

    def increment(self, millis):
        with self._lock:
            self._time.value += millis
        return self.current_time_in_millis()
