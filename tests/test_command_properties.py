from hystrix.properties import CommandProperties


# Utility method for creating baseline properties for unit tests.
def get_unit_test_properties_setter():
    return CommandProperties.setter() \
        .with_execution_timeout_in_milliseconds(1000) \
        .with_execution_isolation_strategy(0) \
        .with_execution_isolation_thread_interrupt_on_timeout(True) \
        .with_circuit_breaker_force_open(False) \
        .with_circuit_breaker_error_threshold_percentage(40) \
        .with_metrics_rolling_statistical_window_in_milliseconds(5000) \
        .with_metrics_rolling_statistical_window_buckets(5) \
        .with_circuit_breaker_request_volume_threshold(0) \
        .with_circuit_breaker_sleep_window_in_milliseconds(5000000) \
        .with_circuit_breaker_enabled(True) \
        .with_request_log_enabled(True) \
        .with_execution_isolation_semaphore_max_concurrent_requests(20) \
        .with_fallback_isolation_semaphore_max_concurrent_requests(10) \
        .with_fallback_enabled(True) \
        .with_circuit_breaker_force_closed(False) \
        .with_metrics_rolling_percentile_enabled(True) \
        .with_request_cache_enabled(True) \
        .with_metrics_rolling_percentile_window_in_milliseconds(60000) \
        .with_metrics_rolling_percentile_window_buckets(12) \
        .with_metrics_rolling_percentile_bucket_size(1000) \
        .with_metrics_health_snapshot_interval_in_milliseconds(0)


class TestPropertiesCommand(CommandProperties):

    def __init__(self, command_name, setter, property_prefix):
        super(TestPropertiesCommand, self).__init__(command_name, setter, property_prefix)


def test_boolean_setter_override1():
    setter = CommandProperties.setter().with_circuit_breaker_force_closed(True)
    properties = TestPropertiesCommand('TEST', setter, 'unitTestPrefix')

    # The setter override should take precedence over default_value
    assert True == properties.circuit_breaker_force_closed()


def test_boolean_setter_override2():
    setter = CommandProperties.setter().with_circuit_breaker_force_closed(False)
    properties = TestPropertiesCommand('TEST', setter, 'unitTestPrefix')

    # The setter override should take precedence over default
    assert False == properties.circuit_breaker_force_closed()


def test_boolean_code_default():
    setter = CommandProperties.setter()
    properties = TestPropertiesCommand('TEST', setter, 'unitTestPrefix')

    assert CommandProperties.default_circuit_breaker_force_closed == properties.circuit_breaker_force_closed()


def test_integer_setter_override():
    setter = CommandProperties.setter().with_metrics_rolling_statistical_window_in_milliseconds(5000)
    properties = TestPropertiesCommand('TEST', setter, 'unitTestPrefix')

    # The setter override should take precedence over default_value
    assert 5000 == properties.metrics_rolling_statistical_window_in_milliseconds()


def test_integer_code_default():
    setter = CommandProperties.setter()
    properties = TestPropertiesCommand('TEST', setter, 'unitTestPrefix')

    assert CommandProperties.default_metrics_rolling_statistical_window == properties.metrics_rolling_statistical_window_in_milliseconds()
