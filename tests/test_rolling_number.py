from hystrix.rolling_number import RollingNumber, RollingNumberEvent

import pytest


def test_create_buckets():
    time = MockedTime()
    counter = RollingNumber(time, 200, 10)

    #  confirm the initial settings
    assert counter.milliseconds == 200
    assert counter.bucket_numbers == 10
    assert counter.buckets_size_in_milliseconds() == 20

    #  we start out with 0 buckets in the queue
    assert counter.buckets.size == 0

    #  add a success in each interval which should result in all 10 buckets
    #  being created with 1 success in each
    for r in range(counter.bucket_numbers):
        counter.increment(RollingNumberEvent.SUCCESS)
        time.increment(counter.buckets_size_in_milliseconds())

    #  confirm we have all 10 buckets
    assert counter.buckets.size == 10

    #  add 1 more and we should still only have 10 buckets since that's the max
    counter.increment(RollingNumberEvent.SUCCESS)
    assert counter.buckets.size == 10


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
        self.time = 0

    def current_time_in_millis(self):
        return self.time

    def increment(self, millis):
        self.time += millis
        return self.time
