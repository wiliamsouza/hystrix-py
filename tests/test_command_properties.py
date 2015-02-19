from hystrix.properties import CommandProperties


# Utility method for creating baseline properties for unit tests.
def get_unit_test_properties_setter():
    return CommandProperties.setter()
        .with_execution_timeout_in_milliseconds(1000)  # when an execution will be timed out
        .with_execution_isolation_strategy(0)  # we want thread execution by default in tests
        .with_execution_isolation_thread_interrupt_on_timeout(True)
        .with_circuit_breaker_force_open(false)  # we don't want short-circuiting by default
        .with_circuit_breaker_error_threshold_percentage(40)  # % of 'marks' that must be failed to trip the circuit
        .with_metrics_rolling_statistical_window_in_milliseconds(5000)  # milliseconds back that will be tracked
        .with_metrics_rolling_statistical_window_buckets(5)  # buckets
        .with_circuit_breaker_request_volume_threshold(0)  # in testing we will not have a threshold unless we're specifically testing that feature
        .with_circuit_breaker_sleep_window_in_milliseconds(5000000)  # milliseconds after tripping circuit before allowing retry (by default set VERY long as we want it to effectively never allow a singleTest for most unit tests)
        .with_circuit_breaker_enabled(True)
        .with_request_log_enabled(True)
        .with_execution_isolation_semaphore_max_concurrent_requests(20)
        .with_fallback_isolation_semaphore_max_concurrent_requests(10)
        .with_fallback_enabled(True)
        .with_circuit_breaker_force_closed(False)
        .with_metrics_rolling_percentile_enabled(True)
        .with_request_cache_enabled(True)
        .with_metrics_rolling_percentile_window_in_milliseconds(60000)
        .with_metrics_rolling_percentile_window_buckets(12)
        .with_metrics_rolling_percentile_bucket_size(1000)
        .with_metrics_health_snapshot_interval_in_milliseconds(0)
