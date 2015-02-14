import pytest

from .utils import MockedTime
from .sample_data import sample_data_holder_1, sample_data_holder_2

from hystrix.rolling_percentile import RollingPercentile, PercentileSnapshot


def test_rolling():
    time = MockedTime()
    percentile = RollingPercentile(time, 60000, 12, 1000, True)
    percentile.add_value(1000)
    percentile.add_value(1000)
    percentile.add_value(1000)
    percentile.add_value(2000)

    assert percentile.buckets.size == 1

    # No bucket turnover yet so percentile not yet generated
    assert percentile.percentile(50) == 0

    time.increment(6000)

    # Still only 1 bucket until we touch it again
    assert percentile.buckets.size == 1

    # A bucket has been created so we have a new percentile
    assert percentile.percentile(50) == 1000

    # Now 2 buckets since getting a percentile causes bucket retrieval
    assert percentile.buckets.size == 2

    percentile.add_value(1000)
    percentile.add_value(500)

    assert percentile.buckets.size == 2

    percentile.add_value(200)
    percentile.add_value(200)
    percentile.add_value(1600)
    percentile.add_value(200)
    percentile.add_value(1600)
    percentile.add_value(1600)

    # We haven't progressed to a new bucket so the percentile should be the
    # same and ignore the most recent bucket
    assert percentile.percentile(50) == 1000

    # Increment to another bucket so we include all of the above in the
    # PercentileSnapshot
    time.increment(6000)

    # The rolling version should have the same data as creating a snapshot
    # like this
    snapshot = PercentileSnapshot(1000, 1000, 1000, 2000, 1000, 500,
                                  200, 200, 1600, 200, 1600, 1600)

    assert snapshot.percentile(0.15) == percentile.percentile(0.15)
    assert snapshot.percentile(0.50) == percentile.percentile(0.50)
    assert snapshot.percentile(0.90) == percentile.percentile(0.90)
    assert snapshot.percentile(0.995) == percentile.percentile(0.995)

    # mean = 1000+1000+1000+2000+1000+500+200+200+1600+200+1600+1600/12
    assert snapshot.mean() == 991


def test_value_is_zero_after_rolling_window_passes_and_no_traffic():
    time = MockedTime()
    percentile = RollingPercentile(time, 60000, 12, 1000, True)
    percentile.add_value(1000)
    percentile.add_value(1000)
    percentile.add_value(1000)
    percentile.add_value(2000)
    percentile.add_value(4000)

    assert percentile.buckets.size == 1

    # No bucket turnover yet so percentile not yet generated
    assert percentile.percentile(50) == 0

    time.increment(6000)

    # Still only 1 bucket until we touch it again
    assert percentile.buckets.size == 1

    # A bucket has been created so we have a new percentile
    assert percentile.percentile(50) == 1500

    # Let 1 minute pass
    time.increment(60000)

    # No data in a minute should mean all buckets are empty (or reset) so we
    # should not have any percentiles
    assert percentile.percentile(50) == 0


def test_sample_data_over_time_1():
    time = MockedTime()
    percentile = RollingPercentile(time, 60000, 12, 1000, True)
    previous_time = 0
    for time_millis, latency in sample_data_holder_1:
        time.increment(time_millis - previous_time)
        previous_time = time_millis
        percentile.add_value(latency)

    print('0.01', percentile.percentile(0.01))
    print('Median', percentile.percentile(50))
    print('90th', percentile.percentile(90))
    print('99th', percentile.percentile(99))
    print('99.5th', percentile.percentile(99.5))
    print('99.99', percentile.percentile(99.99))

    print('Median', percentile.percentile(50))
    print('Median', percentile.percentile(50))
    print('Median', percentile.percentile(50))

    # In a loop as a use case was found where very different values were
    # calculated in subsequent requests.
    for _ in range(10):
        percentile50 = percentile.percentile(50)
        if percentile50 > 5:
            pytest.fail('We expect around 2 but got: {}'.format(percentile50))

        percentile995 = percentile.percentile(99.5)
        if percentile995 < 20:
            msg = 'We expect to see some high values over 20 but got: {}'
            pytest.fail(msg.format(percentile995))


def test_sample_data_over_time_2():
    time = MockedTime()
    percentile = RollingPercentile(time, 60000, 12, 1000, True)
    previous_time = 0
    for time_millis, latency in sample_data_holder_2:
        time.increment(time_millis - previous_time)
        previous_time = time_millis
        percentile.add_value(latency)

    print('0.01', percentile.percentile(0.01))
    print('Median', percentile.percentile(50))
    print('90th', percentile.percentile(90))
    print('99th', percentile.percentile(99))
    print('99.5th', percentile.percentile(99.5))
    print('99.99', percentile.percentile(99.99))

    percentile50 = percentile.percentile(50)
    if percentile50 > 90 or percentile50 < 50:
        pytest.fail('We expect around 60-70 but got: {}'.format(percentile50))

    percentile99 = percentile.percentile(99)
    if percentile99 < 400:
        msg = 'We expect to see some high values over 400 but got: {}'
        pytest.fail(msg.format(percentile99))


def test_percentile_algorithm_media1():
    snapshot = PercentileSnapshot(100, 100, 100, 100, 200, 200,
                                  200, 300, 300, 300, 300)
    assert snapshot.percentile(50) == 200


def test_percentile_algorithm_media2():
    snapshot = PercentileSnapshot(100, 100, 100, 100, 100, 100,
                                  100, 100, 100, 100, 500)
    assert snapshot.percentile(50) == 100


def test_percentile_algorithm_media3():
    snapshot = PercentileSnapshot(50, 75, 100, 125, 160, 170,
                                  180, 200, 210, 300, 500)
    assert snapshot.percentile(50) == 175


def test_percentile_algorithm_media4():
    ''' Unsorted so it is expected to sort it for us. '''
    snapshot = PercentileSnapshot(300, 75, 125, 500, 100, 160,
                                  180, 200, 210, 50, 170)
    assert snapshot.percentile(50) == 175


def test_percentile_algorithm_extremes():
    ''' Unsorted so it is expected to sort it for us. '''
    snapshot = PercentileSnapshot(2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
                                  2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
                                  2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
                                  800, 768, 657, 700, 867)

    print('0.01', snapshot.percentile(0.01))
    print('10th', snapshot.percentile(10))
    print('Median', snapshot.percentile(50))
    print('75th', snapshot.percentile(75))
    print('90th', snapshot.percentile(90))
    print('99th', snapshot.percentile(99))
    print('99.5th', snapshot.percentile(99.5))
    print('99.99', snapshot.percentile(99.99))

    assert snapshot.percentile(50) == 2
    assert snapshot.percentile(10) == 2
    assert snapshot.percentile(75) == 2

    if snapshot.percentile(95) < 600:
        msg = 'We expect 90th to be over 600 to show the extremes but got: {}'
        pytest.fail(msg.format(snapshot.percentile(95)))

    if snapshot.percentile(99) < 600:
        msg = 'We expect 99th to be over 600 to show the extremes but got: {}'
        pytest.fail(msg.format(snapshot.percentile(99)))


def percentile_for_values(*values):
    return PercentileSnapshot(*values)


def test_percentile_algorithm_high_percentile():
    snapshot = percentile_for_values(1, 2, 3)
    assert snapshot.percentile(50) == 2
    assert snapshot.percentile(75) == 3


def test_percentile_algorithm_low_percentile():
    snapshot = percentile_for_values(1, 2)
    assert snapshot.percentile(25) == 1
    assert snapshot.percentile(75) == 2


def test_percentile_algorithm_percentiles():
    snapshot = percentile_for_values(10, 30, 20, 40)

    assert snapshot.percentile(30) == 22
    assert snapshot.percentile(25) == 20
    assert snapshot.percentile(75) == 40
    assert snapshot.percentile(50) == 30

    assert snapshot.percentile(-1) == 10
    assert snapshot.percentile(101) == 40


def test_percentile_algorithm_NIST_example():
    snapshot = percentile_for_values(951772, 951567, 951937, 951959, 951442,
                                     950610, 951591, 951195, 951772, 950925,
                                     951990, 951682)
    assert snapshot.percentile(90) == 951983
    assert snapshot.percentile(100) == 951990


def test_does_nothing_when_disabled():
    time = MockedTime()
    percentile = RollingPercentile(time, 60000, 12, 1000, False)
    previous_time = 0
    for time_millis, latency in sample_data_holder_2:
        time.increment(time_millis - previous_time)
        previous_time = time_millis
        percentile.add_value(latency)

    assert percentile.percentile(50) == -1
    assert percentile.percentile(75) == -1
    assert percentile.mean() == -1
