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


def test_increment_in_multiple_buckets():
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
    counter.increment(RollingNumberEvent.TIMEOUT)
    counter.increment(RollingNumberEvent.SHORT_CIRCUITED)

    # Sleep to get to a new bucket
    time.increment(counter.buckets_size_in_milliseconds() * 3)

    # Increment
    counter.increment(RollingNumberEvent.SUCCESS)
    counter.increment(RollingNumberEvent.SUCCESS)
    counter.increment(RollingNumberEvent.FAILURE)
    counter.increment(RollingNumberEvent.FAILURE)
    counter.increment(RollingNumberEvent.FAILURE)
    counter.increment(RollingNumberEvent.TIMEOUT)
    counter.increment(RollingNumberEvent.SHORT_CIRCUITED)

    # Confirm we have 4 bucket
    assert counter.buckets.size == 4

    # The count of the last buckets
    assert counter.buckets.last().adder(RollingNumberEvent.SUCCESS).sum() == 2
    assert counter.buckets.last().adder(RollingNumberEvent.FAILURE).sum() == 3
    assert counter.buckets.last().adder(RollingNumberEvent.TIMEOUT).sum() == 1
    assert counter.buckets.last().adder(RollingNumberEvent.SHORT_CIRCUITED).sum() == 1

    # The total count
    assert counter.rolling_sum(RollingNumberEvent.SUCCESS) == 6
    assert counter.rolling_sum(RollingNumberEvent.FAILURE) == 5
    assert counter.rolling_sum(RollingNumberEvent.TIMEOUT) == 3
    assert counter.rolling_sum(RollingNumberEvent.SHORT_CIRCUITED) == 2

    # Wait until window passes
    time.increment(counter.milliseconds)

    # Increment
    counter.increment(RollingNumberEvent.SUCCESS)

    # The total count should now include only the last bucket after a reset
    # since the window passed
    assert counter.rolling_sum(RollingNumberEvent.SUCCESS) == 1
    assert counter.rolling_sum(RollingNumberEvent.FAILURE) == 0
    assert counter.rolling_sum(RollingNumberEvent.TIMEOUT) == 0
    assert counter.rolling_sum(RollingNumberEvent.SHORT_CIRCUITED) == 0


def test_success():
    counter_event(RollingNumberEvent.SUCCESS)


def test_failure():
    counter_event(RollingNumberEvent.FAILURE)


def test_timeout():
    counter_event(RollingNumberEvent.TIMEOUT)


def test_short_circuited():
    counter_event(RollingNumberEvent.SHORT_CIRCUITED)


def test_thread_pool_rejected():
    counter_event(RollingNumberEvent.THREAD_POOL_REJECTED)


def test_fallback_success():
    counter_event(RollingNumberEvent.FALLBACK_SUCCESS)


def test_fallback_failure():
    counter_event(RollingNumberEvent.FALLBACK_FAILURE)


def test_fallback_regection():
    counter_event(RollingNumberEvent.FALLBACK_REJECTION)


def test_exception_throw():
    counter_event(RollingNumberEvent.EXCEPTION_THROWN)


def test_thread_execution():
    counter_event(RollingNumberEvent.THREAD_EXECUTION)


def test_collapsed():
    counter_event(RollingNumberEvent.COLLAPSED)


def test_response_from_cache():
    counter_event(RollingNumberEvent.RESPONSE_FROM_CACHE)


def test_counter_retrieval_refreshes_buckets():
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

    # Sleep to get to a new bucketV
    time.increment(counter.buckets_size_in_milliseconds() * 3)

    # We should have 1 bucket since nothing has triggered the update of
    # buckets in the elapsed time
    assert counter.buckets.size == 1

    # The total counts
    assert counter.rolling_sum(RollingNumberEvent.SUCCESS) == 4
    assert counter.rolling_sum(RollingNumberEvent.FAILURE) == 2

    # We should have 4 buckets as the counter should have triggered
    # the buckets being created to fill in time
    assert counter.buckets.size == 4

    # Wait until window passes
    time.increment(counter.milliseconds)

    # The total counts should all be 0 (and the buckets cleared by the get,
    #not only increment)
    assert counter.rolling_sum(RollingNumberEvent.SUCCESS) == 0
    assert counter.rolling_sum(RollingNumberEvent.FAILURE) == 0

    # Increment
    counter.increment(RollingNumberEvent.SUCCESS)

    # The total count should now include only the last bucket after a reset
    # since the window passed
    assert counter.rolling_sum(RollingNumberEvent.SUCCESS) == 1
    assert counter.rolling_sum(RollingNumberEvent.FAILURE) == 0


def test_update_max_1():
    time = MockedTime()
    counter = RollingNumber(time, 200, 10)

    # We start out with 0 buckets in the queue
    assert counter.buckets.size == 0

    # Increment
    counter.update_rolling_max(RollingNumberEvent.THREAD_MAX_ACTIVE, 10)

    # We should have 1
    assert counter.buckets.size == 1

    # The count should be 10
    assert counter.buckets.last().max_updater(RollingNumberEvent.THREAD_MAX_ACTIVE).max() == 10
    assert counter.rolling_max(RollingNumberEvent.THREAD_MAX_ACTIVE) == 10

    # Sleep to get to a new bucket
    time.increment(counter.buckets_size_in_milliseconds() * 3)

    # Increment again is latest bucket
    counter.update_rolling_max(RollingNumberEvent.THREAD_MAX_ACTIVE, 20)

    # We should have 4
    assert counter.buckets.size == 4

    # The max
    assert counter.buckets.last().max_updater(RollingNumberEvent.THREAD_MAX_ACTIVE).max() == 20

    # Count per buckets
    values = counter.get_values(RollingNumberEvent.THREAD_MAX_ACTIVE)
    assert values[0] == 20  # Latest bucket
    assert values[1] == 0
    assert values[2] == 0
    assert values[3] == 10  # Oldest bucket


def test_update_max_2():
    time = MockedTime()
    counter = RollingNumber(time, 200, 10)

    # We start out with 0 buckets in the queue
    assert counter.buckets.size == 0

    # Increment
    counter.update_rolling_max(RollingNumberEvent.THREAD_MAX_ACTIVE, 10)
    counter.update_rolling_max(RollingNumberEvent.THREAD_MAX_ACTIVE, 30)
    counter.update_rolling_max(RollingNumberEvent.THREAD_MAX_ACTIVE, 20)

    # We should have 1
    assert counter.buckets.size == 1

    # The count should be 30
    assert counter.buckets.last().max_updater(RollingNumberEvent.THREAD_MAX_ACTIVE).max() == 30
    assert counter.rolling_max(RollingNumberEvent.THREAD_MAX_ACTIVE) == 30

    # Sleep to get to a new bucket
    time.increment(counter.buckets_size_in_milliseconds() * 3)

    # Increment again is latest bucket
    counter.update_rolling_max(RollingNumberEvent.THREAD_MAX_ACTIVE, 30)
    counter.update_rolling_max(RollingNumberEvent.THREAD_MAX_ACTIVE, 30)
    counter.update_rolling_max(RollingNumberEvent.THREAD_MAX_ACTIVE, 50)

    # We should have 4
    assert counter.buckets.size == 4

    # The count
    assert counter.buckets.last().max_updater(RollingNumberEvent.THREAD_MAX_ACTIVE).max() == 50
    assert counter.value_of_latest_bucket(RollingNumberEvent.THREAD_MAX_ACTIVE) == 50

    # Values per buckets
    values = counter.get_values(RollingNumberEvent.THREAD_MAX_ACTIVE)
    assert values[0] == 50  # Latest bucket
    assert values[1] == 0
    assert values[2] == 0
    assert values[3] == 30  # Oldest bucket


def test_max_value():
    time = MockedTime()
    counter = RollingNumber(time, 200, 10)
    # TODO: Change tests to use this aproache for events
    event = RollingNumberEvent.THREAD_MAX_ACTIVE

    # We start out with 0 buckets in the queue
    assert counter.buckets.size == 0

    # Increment
    counter.update_rolling_max(event, 10)

    # Sleep to get to a new bucket
    time.increment(counter.buckets_size_in_milliseconds())

    # Increment
    counter.update_rolling_max(event, 30)

    # Sleep to get to a new bucket
    time.increment(counter.buckets_size_in_milliseconds())

    # Increment
    counter.update_rolling_max(event, 40)

    # Sleep to get to a new bucket
    time.increment(counter.buckets_size_in_milliseconds())

    # Try Decrement
    counter.update_rolling_max(event, 15)

    # The count should be max
    counter.update_rolling_max(event, 40)


def test_empty_sum():
    time = MockedTime()
    counter = RollingNumber(time, 200, 10)
    event = RollingNumberEvent.COLLAPSED
    assert counter.rolling_sum(event) == 0


def test_empty_max():
    time = MockedTime()
    counter = RollingNumber(time, 200, 10)
    event = RollingNumberEvent.THREAD_MAX_ACTIVE
    assert counter.rolling_max(event) == 0


def test_empty_latest_value():
    time = MockedTime()
    counter = RollingNumber(time, 200, 10)
    event = RollingNumberEvent.THREAD_MAX_ACTIVE
    assert counter.value_of_latest_bucket(event) == 0


def test_rolling():
    time = MockedTime()
    counter = RollingNumber(time, 20, 2)
    event = RollingNumberEvent.THREAD_MAX_ACTIVE
    assert counter.value_of_latest_bucket(event) == 0

    for i in range(20):
        counter.current_bucket()
        time.increment(counter.buckets_size_in_milliseconds())

    assert len(counter.get_values(event)) == 2

    counter.value_of_latest_bucket(event)


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


def counter_event(event):
    time = MockedTime()
    counter = RollingNumber(time, 200, 10)

    # We start out with 0 buckets in the queue
    assert counter.buckets.size == 0

    # We start out with 0 sum
    assert counter.rolling_sum(event) == 0

    # Increment
    counter.increment(event)

    # We shoud have 1 bucket
    assert counter.buckets.size == 1

    # The count should be 1
    assert counter.buckets.last().adder(event).sum() == 1
    assert counter.rolling_sum(event) == 1

    # Sleep to get to a new bucket
    time.increment(counter.buckets_size_in_milliseconds() * 3)

    # Incremenet again in latest bucket
    counter.increment(event)

    # We should have 4 buckets
    assert counter.buckets.size == 4

    # The count of the last bucket
    assert counter.buckets.last().adder(event).sum() == 1

    # The total count
    assert counter.rolling_sum(event) == 2
