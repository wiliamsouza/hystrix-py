from hystrix.metrics import Metrics
from hystrix.command_properties import CommandProperties
from hystrix.rolling_number import RollingNumber, RollingNumberEvent

setter = CommandProperties.setter()
properties = CommandProperties('TEST', setter, 'unit_test_prefix')
counter = RollingNumber(properties.metrics_rolling_statistical_window_in_milliseconds(),
                        properties.metrics_rolling_statistical_window_buckets())


def test_metrics_cumulative_count():
    metrics = Metrics(counter)
    assert metrics.cumulative_count(RollingNumberEvent.THREAD_MAX_ACTIVE) == 0


def test_metrics_rolling_count():
    metrics = Metrics(counter)
    assert metrics.rolling_count(RollingNumberEvent.SUCCESS) == 0
