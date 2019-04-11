from hystrix.command_properties import CommandProperties


# TODO: Move this to utils.py file
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


# TODO: Move this to utils.py file
# Return a static representation of the properties with values from the Builder
# so that UnitTests can create properties that are not affected by the actual
# implementations which pick up their values dynamically.
# NOTE: This only work because in CommandProperties the setter override should
#       take precedence over default_value
def as_mock(setter):
    return CommandProperties('TEST', setter, 'unit_test_prefix')


class PropertiesCommandTest(CommandProperties):

    def __init__(self, command_name, setter, property_prefix):
        super(PropertiesCommandTest, self).__init__(command_name, setter, property_prefix)


def test_boolean_setter_override1():
    setter = CommandProperties.setter().with_circuit_breaker_force_closed(True)
    properties = PropertiesCommandTest('TEST', setter, 'unitTestPrefix')

    # The setter override should take precedence over default_value
    assert True == properties.circuit_breaker_force_closed()


def test_boolean_setter_override2():
    setter = CommandProperties.setter().with_circuit_breaker_force_closed(False)
    properties = PropertiesCommandTest('TEST', setter, 'unitTestPrefix')

    # The setter override should take precedence over default
    assert False == properties.circuit_breaker_force_closed()


def test_boolean_code_default():
    setter = CommandProperties.setter()
    properties = PropertiesCommandTest('TEST', setter, 'unitTestPrefix')

    assert CommandProperties.default_circuit_breaker_force_closed == properties.circuit_breaker_force_closed()


def test_integer_setter_override():
    setter = CommandProperties.setter().with_metrics_rolling_statistical_window_in_milliseconds(5000)
    properties = PropertiesCommandTest('TEST', setter, 'unitTestPrefix')

    # The setter override should take precedence over default_value
    assert 5000 == properties.metrics_rolling_statistical_window_in_milliseconds()


def test_integer_code_default():
    setter = CommandProperties.setter()
    properties = PropertiesCommandTest('TEST', setter, 'unitTestPrefix')

    result1 = CommandProperties.default_metrics_rolling_statistical_window
    result2 = properties.metrics_rolling_statistical_window_in_milliseconds()
    assert result1 == result2
