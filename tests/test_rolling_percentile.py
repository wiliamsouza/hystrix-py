from .utils import MockedTime

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
    percentile.add_value(1000)

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
