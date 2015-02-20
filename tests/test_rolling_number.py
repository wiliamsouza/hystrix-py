import pytest

from .utils import MockedTime

from hystrix.rolling_number import RollingNumber, RollingNumberEvent


def test_create_buckets():
    _time = MockedTime()
    counter = RollingNumber(200, 10, _time=_time)

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
        _time.increment(counter.buckets_size_in_milliseconds())

    # confirm we have all 10 buckets
    assert counter.buckets.size == 10

    # add 1 more and we should still only have 10 buckets since that's the max
    counter.increment(RollingNumberEvent.SUCCESS)
    assert counter.buckets.size == 10


def test_reset_buckets():
    _time = MockedTime()
    counter = RollingNumber(200, 10, _time=_time)

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
    _time = MockedTime()
    counter = RollingNumber(200, 10, _time=_time)

    # We start out with 0 buckets in the queue
    assert counter.buckets.size == 0

    # Add 1
    counter.increment(RollingNumberEvent.SUCCESS)

    # Confirm we have 1 bucket
    assert counter.buckets.size == 1

    # Wait past 3 bucket time periods (the 1st bucket then 2 empty ones)
    _time.increment(counter.buckets_size_in_milliseconds() * 3)

    # Add another
    counter.increment(RollingNumberEvent.SUCCESS)

    # We should have 4 (1 + 2 empty + 1 new one) buckets
    assert counter.buckets.size == 4


def test_increment_in_single_bucket():
    _time = MockedTime()
    counter = RollingNumber(200, 10, _time=_time)

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
    _time = MockedTime()
    counter = RollingNumber(200, 10, _time=_time)

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
    _time.increment(counter.buckets_size_in_milliseconds() * 3)

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
    _time.increment(counter.milliseconds)

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
    _time = MockedTime()
    counter = RollingNumber(200, 10, _time=_time)

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
    _time.increment(counter.buckets_size_in_milliseconds() * 3)

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
    _time.increment(counter.milliseconds)

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
    _time = MockedTime()
    counter = RollingNumber(200, 10, _time=_time)

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
    _time.increment(counter.buckets_size_in_milliseconds() * 3)

    # Increment again is latest bucket
    counter.update_rolling_max(RollingNumberEvent.THREAD_MAX_ACTIVE, 20)

    # We should have 4
    assert counter.buckets.size == 4

    # The max
    assert counter.buckets.last().max_updater(RollingNumberEvent.THREAD_MAX_ACTIVE).max() == 20

    # Count per buckets
    values = counter.values(RollingNumberEvent.THREAD_MAX_ACTIVE)
    assert values[0] == 20  # Latest bucket
    assert values[1] == 0
    assert values[2] == 0
    assert values[3] == 10  # Oldest bucket


def test_update_max_2():
    _time = MockedTime()
    counter = RollingNumber(200, 10, _time=_time)

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
    _time.increment(counter.buckets_size_in_milliseconds() * 3)

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
    values = counter.values(RollingNumberEvent.THREAD_MAX_ACTIVE)
    assert values[0] == 50  # Latest bucket
    assert values[1] == 0
    assert values[2] == 0
    assert values[3] == 30  # Oldest bucket


def test_max_value():
    _time = MockedTime()
    counter = RollingNumber(200, 10, _time=_time)
    # TODO: Change tests to use this aproache for events
    event = RollingNumberEvent.THREAD_MAX_ACTIVE

    # We start out with 0 buckets in the queue
    assert counter.buckets.size == 0

    # Increment
    counter.update_rolling_max(event, 10)

    # Sleep to get to a new bucket
    _time.increment(counter.buckets_size_in_milliseconds())

    # Increment
    counter.update_rolling_max(event, 30)

    # Sleep to get to a new bucket
    _time.increment(counter.buckets_size_in_milliseconds())

    # Increment
    counter.update_rolling_max(event, 40)

    # Sleep to get to a new bucket
    _time.increment(counter.buckets_size_in_milliseconds())

    # Try Decrement
    counter.update_rolling_max(event, 15)

    # The count should be max
    counter.update_rolling_max(event, 40)


def test_empty_sum():
    _time = MockedTime()
    counter = RollingNumber(200, 10, _time=_time)
    event = RollingNumberEvent.COLLAPSED
    assert counter.rolling_sum(event) == 0


def test_empty_max():
    _time = MockedTime()
    counter = RollingNumber(200, 10, _time=_time)
    event = RollingNumberEvent.THREAD_MAX_ACTIVE
    assert counter.rolling_max(event) == 0


def test_empty_latest_value():
    _time = MockedTime()
    counter = RollingNumber(200, 10, _time=_time)
    event = RollingNumberEvent.THREAD_MAX_ACTIVE
    assert counter.value_of_latest_bucket(event) == 0


def test_rolling():
    _time = MockedTime()
    counter = RollingNumber(20, 2, _time=_time)
    event = RollingNumberEvent.THREAD_MAX_ACTIVE

    assert counter.cumulative_sum(event) == 0

    # Iterate over 20 buckets on a queue sized for 2
    for i in range(20):
        counter.current_bucket()
        _time.increment(counter.buckets_size_in_milliseconds())

        assert len(counter.values(event)) == 2

        counter.value_of_latest_bucket(event)


def test_cumulative_counter_after_rolling():
    _time = MockedTime()
    counter = RollingNumber(20, 2, _time=_time)
    event = RollingNumberEvent.SUCCESS

    assert counter.cumulative_sum(event) == 0

    # Iterate over 20 buckets on a queue sized for 2
    for i in range(20):
        counter.increment(event)
        _time.increment(counter.buckets_size_in_milliseconds())

        assert len(counter.values(event)) == 2

        counter.value_of_latest_bucket(event)

    # Cumulative count should be 20 (for the number of loops above) regardless
    # of buckets rolling
    assert counter.cumulative_sum(event) == 20


def test_cumulative_counter_after_rolling_and_reset():
    _time = MockedTime()
    counter = RollingNumber(20, 2, _time=_time)
    event = RollingNumberEvent.SUCCESS

    assert counter.cumulative_sum(event) == 0

    # Iterate over 20 buckets on a queue sized for 2
    for i in range(20):
        counter.increment(event)
        _time.increment(counter.buckets_size_in_milliseconds())

        assert len(counter.values(event)) == 2

        counter.value_of_latest_bucket(event)

        # simulate a reset occurring every once in a while
        # so we ensure the absolute sum is handling it okay
        if i == 5 or i == 15:
            counter.reset()

    # Cumulative count should be 20 (for the number of loops above) regardless
    # of buckets rolling
    assert counter.cumulative_sum(event) == 20


def test_cumulative_counter_after_rolling_and_reset2():
    _time = MockedTime()
    counter = RollingNumber(20, 2, _time=_time)
    event = RollingNumberEvent.SUCCESS

    assert counter.cumulative_sum(event) == 0

    counter.increment(event)
    counter.increment(event)
    counter.increment(event)

    # Iterate over 20 buckets on a queue sized for 2
    for i in range(20):
        _time.increment(counter.buckets_size_in_milliseconds())

        # simulate a reset occurring every once in a while
        # so we ensure the absolute sum is handling it okay
        if i == 5 or i == 15:
            counter.reset()

    # No increments during the loop, just some before and after
    counter.increment(event)
    counter.increment(event)

    # Cumulative count should be 5 regardless of buckets rolling
    assert counter.cumulative_sum(event) == 5


def test_cumulative_counter_after_rolling_and_reset3():
    _time = MockedTime()
    counter = RollingNumber(20, 2, _time=_time)
    event = RollingNumberEvent.SUCCESS

    assert counter.cumulative_sum(event) == 0

    counter.increment(event)
    counter.increment(event)
    counter.increment(event)

    # Iterate over 20 buckets on a queue sized for 2
    for i in range(20):
        _time.increment(counter.buckets_size_in_milliseconds())

    # Since we are rolling over the buckets it should reset naturally

    # No increments during the loop, just some before and after
    counter.increment(event)
    counter.increment(event)

    # Cumulative count should be 5 regardless of buckets rolling
    assert counter.cumulative_sum(event) == 5


def test_milliseconds_buckets_size_error():
    _time = MockedTime()

    with pytest.raises(Exception):
        RollingNumber(100, 11, _time=_time)


def test_rolling_number_event_is_counter():
    event = RollingNumberEvent(RollingNumberEvent.SUCCESS)
    assert event.is_counter() is True


def test_rolling_number_event_is_max_updater():
    event = RollingNumberEvent(RollingNumberEvent.THREAD_MAX_ACTIVE)
    assert event.is_max_updater() is True


def counter_event(event):
    _time = MockedTime()
    counter = RollingNumber(200, 10, _time=_time)

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
    _time.increment(counter.buckets_size_in_milliseconds() * 3)

    # Incremenet again in latest bucket
    counter.increment(event)

    # We should have 4 buckets
    assert counter.buckets.size == 4

    # The count of the last bucket
    assert counter.buckets.last().adder(event).sum() == 1

    # The total count
    assert counter.rolling_sum(event) == 2
