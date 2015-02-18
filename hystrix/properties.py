from __future__ import absolute_import
import logging

log = logging.getLogger(__name__)


class CommandProperties(object):
    """ Properties for instances of :class:`hystrix.command.Command`
    """

    # Default values

    # 10000 = 10 seconds (and default of 10 buckets so each bucket is 1
    # second)
    default_metrics_rolling_statistical_window_in_milliseconds = 10000

    # 10 buckets in a 10 second window so each bucket is 1 second
    default_metrics_rolling_statistical_window_buckets = 10

    # 20 requests in 10 seconds must occur before statistics matter
    default_circuit_breaker_request_volume_threshold = 20

    # 5000 = 5 seconds that we will sleep before trying again after tripping
    # the circuit
    default_circuit_breaker_wleep_window_in_milliseconds = 5000

    # 50 = if 50%+ of requests in 10 seconds are failures or latent when we
    # will trip the circuit
    default_circuit_breaker_error_threshold_percentage = 50

    # If ``False`` we want to allow traffic.
    default_circuit_breaker_force_open = False

    # If ``False`` ignore errors
    default_circuit_breaker_force_closed = False

    # 1000 = 1 second timeout
    default_execution_timeout_in_milliseconds = 1000

    # Whether a command should be executed in a separate thread or not
    default_execution_isolation_strategy = 0

    # Wheather a thread should interrupt on timeout.
    default_execution_isolation_thread_interrupt_on_timeout = True

    # Wheather rolling percentile should be enabled.
    default_metrics_rolling_percentile_enabled = True

    # Wheather request cache should be enabled
    default_request_cache_enabled = True

    # Default fallback isolation semaphore max concurrent requests
    default_fallback_isolation_semaphore_max_concurrent_requests = 10

    # Wheather fallback should be enabled
    default_fallback_enabled = True

    # Default execution isolation semaphore max concurrent requests
    default_execution_isolation_semaphore_max_concurrent_requests = 10

    # Wheather request log should be enabled
    default_request_log_enabled = True

    # Wheather circuit breaker should be enabled
    default_circuit_breaker_enabled = True

    # Default to 1 minute for
    # :class:`hystrix.rolling_percentile._rolling_percentile`
    default_metrics_rolling_percentile_window = 60000

    # Default to 6 buckets (10 seconds each in 60 second window)
    default_metrics_rolling_percentile_window_buckets = 6

    # Default to 100 values max per bucket
    default_metrics_rolling_percentile_bucket_size = 100

    # Default to 500ms as max frequency between allowing snapshots of health
    # (error percentage etc)
    default_metrics_health_snapshot_interval_in_milliseconds = 500

    def __init__(self, key, builder, property_prefix):
        self.command_key = key
        self.property_prefix = property_prefix

        # Whether circuit breaker should be enabled
        self.circuit_breaker_enabled = \
            self.get_property(
                self.property_prefix, self.command_key,
                'circuit_breaker.enabled',
                builder.get_circuit_breaker_enabled(),
                self.default_circuit_breaker_enabled)

        # Number of requests that must be made within a statisticalWindow
        # before open/close decisions are made using stats
        self.circuit_breaker_request_volume_threshold = \
            self.get_property(
                self.property_prefix, self.command_key,
                'circuit_breaker.request_volume_threshold',
                builder.get_circuit_breaker_request_volume_threshold(),
                self.default_circuit_breaker_request_volume_threshold)

        # Milliseconds after tripping circuit before allowing retry
        self.circuit_breaker_sleep_window_in_milliseconds = \
            self.get_property(
                self.property_prefix, self.command_key,
                'circuit_breaker.sleep_window_in_milliseconds',
                builder.get_circuit_breaker_sleep_window_in_milliseconds(),
                self.default_circuit_breaker_sleep_window_in_milliseconds)

        # % of 'marks' that must be failed to trip the circuit
        self.circuit_breaker_error_threshold_percentage = \
            self.get_property(
                self.property_prefix, self.command_key,
                'circuit_breaker.error_threshold_percentage',
                builder.get_circuit_breaker_error_threshold_percentage(),
                self.default_circuit_breaker_error_threshold_percentage)

        # A property to allow forcing the circuit open (stopping all requests)
        self.circuit_breaker_force_open = \
            self.get_property(
                self.property_prefix, self.command_key,
                'circuit_breaker.force_open',
                builder.get_circuit_breaker_force_open(),
                self.default_circuit_breaker_force_open)

        # a property to allow ignoring errors and therefore never trip 'open'
        # (ie. allow all traffic through)
        self.circuit_breaker_force_closed = \
            self.get_property(
                self.property_prefix, self.command_key,
                'circuit_breaker.force_closed',
                builder.get_circuit_breaker_force_closed(),
                self.default_circuit_breaker_forcer_closed)

        # Whether a command should be executed in a separate thread or not
        self.execution_isolation_strategy = \
            self.get_property(
                self.property_prefix, self.command_key,
                'execution.isolation.strategy',
                builder.get_execution_isolation_strategy(),
                self.efault_execution_isolation_strategy)

        # Timeout value in milliseconds for a command
        self.execution_timeout_in_milliseconds = \
            self.get_property(
                self.property_prefix, key,
                'execution.isolation.thread.timeout_in_milliseconds',
                builder.get_execution_timeout_in_milliseconds(),
                self.default_execution_timeout_in_milliseconds)

        # Whether an underlying Future/Thread
        # (when runInSeparateThread == true) should be interrupted after a
        # timeout
        self.execution_isolation_thread_interrupt_on_timeout = \
            self.get_property(
                self.property_prefix, self.command_key,
                'execution.isolation.thread.interrupt_on_timeout',
                builder.get_execution_isolation_thread_interrupt_on_timeout(),
                self.default_execution_isolation_thread_interrupt_on_timeout)

        # Number of permits for execution semaphore
        self.execution_isolation_semaphore_max_concurrent_requests = \
            self.get_property(
                self.property_prefix, self.command_key,
                'execution.isolation.semaphore.max_concurrent_requests',
                builder.get_execution_isolation_semaphore_max_concurrent_requests(),
                self.default_execution_isolation__semaphore_max_concurrent_requests)

        # Number of permits for fallback semaphore
        self.fallback_isolation_semaphore_max_concurrent_requests = \
            self.get_property(
                self.property_prefix, self.command_key,
                'fallback.isolation.semaphore.max_concurrent_requests',
                builder.get_fallback_isolation_semaphore_max_concurrent_requests(),
                self.default_fallback_isolation_semaphore_max_concurrent_requests)

        # Whether fallback should be attempted
        self.fallback_enabled = \
            self.get_property(
                self.property_prefix, self.command_key, 'fallback.enabled',
                builder.get_fallback_enabled(), self.default_fallback_enabled)

        #  Milliseconds back that will be tracked
        self.metrics_rolling_statistical_window_in_milliseconds = \
            self.get_property(
                self.property_prefix, self.command_key,
                'metrics.rolling_stats.time_in_milliseconds',
                builder.get_metrics_rolling_statistical_window_in_milliseconds(),
                self.default_metrics_rolling_statistical_window_in_milliseconds)

        # number of buckets in the statisticalWindow
        self.metrics_rolling_statistical_window_buckets = \
            self.get_property(
                self.property_prefix, self.command_key,
                'metrics.rolling_stats.num_buckets',
                builder.get_metrics_rolling_statistical_window_buckets(),
                self.default_metrics_rolling_statistical_window_buckets)

        # Whether monitoring should be enabled (SLA and Tracers)
        self.metrics_rolling_percentile_enabled = \
            self.get_property(
                self.property_prefix,
                self.command_key, 'metrics.rolling_percentile.enabled',
                builder.get_metrics_rolling_percentile_enabled(),
                self.default_metrics_rolling_percentile_enabled)

        # Number of milliseconds that will be tracked in
        # :class:`hystrix.rolling_percentile.RollingPercentile`
        self.metrics_rolling_percentile_window_in_milliseconds = \
            self.get_property(
                self.property_prefix, self.command_key,
                'metrics.rolling_percentile.time_in_milliseconds',
                builder.get_metrics_rolling_percentile_window_in_milliseconds(),
                self.default_metrics_rolling_percentile_window)

        # Number of buckets percentileWindow will be divided into
        self.metrics_rolling_percentile_window_buckets = \
            self.get_property(
                self.property_prefix, self.command_key,
                'metrics.rolling_percentile.num_buckets',
                builder.get_metrics_rolling_percentile_window_buckets(),
                self.default_metrics_rolling_percentile_window_buckets)

        # How many values will be stored in each
        # :attr:`percentile_window_bucket`
        self.metrics_rolling_percentile_bucket_size = \
            self.get_property(
                self.property_prefix, self.command_key,
                'metrics.rolling_percentile.bucket_size',
                builder.get_metrics_rolling_percentile_bucket_size(),
                self.default_metrics_rolling_percentile_bucket_size)

        # Time between health snapshots
        self.metrics_health_snapshot_interval_in_milliseconds = \
            self.get_property(
                self.property_prefix, self.command_key,
                'metrics.health_snapshot.interval_in_milliseconds',
                builder.get_metrics_health_snapshot_interval_in_milliseconds(),
                self.default_metrics_health_snapshot_interval_in_milliseconds)

        # Whether command request logging is enabled
        self.request_log_enabled = \
            self.get_property(
                property_prefix, self.command_key, 'request_log.enabled',
                builder.get_request_log_enabled(),
                self.default_request_log_enabled)

        # Whether request caching is enabled
        self.request_cache_enabled = \
            self.get_property(
                self.property_prefix, self.command_key,
                'request_cache.enabled',
                builder.get_request_cache_enabled(),
                self.default_request_cache_enabled)

        # threadpool doesn't have a global override, only instance level
        # makes sense
        # self.execution_isolation_thread_pool_key_override = \
        #    as_property(
        #        DynamicStringProperty(
        #            '{}.command.{}.thread_pool_key_override'.format(
        #                self.property_prefix, self.command_key), None))

    # TODO: Fix this for now it just return default values
    def get_property(self, property_prefix, command_key, instance_property,
                     builder_override_value, default_value):
        """ Get property from a networked plugin
        """
        return default_value
