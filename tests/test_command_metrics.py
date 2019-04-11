import time

from hystrix.command import Command
from hystrix.command_metrics import CommandMetrics
from hystrix.command_properties import CommandProperties
from hystrix.strategy.eventnotifier.event_notifier_default import (
    EventNotifierDefault)

from .test_command_properties import get_unit_test_properties_setter, as_mock

setter = CommandProperties.setter()
properties = CommandProperties('TEST', setter, 'unit_test_prefix')
event_notifier = EventNotifierDefault.get_instance()


def test_default_command_metrics_key():
    class Test(CommandMetrics):
        pass

    commandmetrics = Test(None, 'command_group', None, properties,
                          event_notifier)
    assert commandmetrics.command_metrics_key == 'TestCommandMetrics'


def test_manual_command_metrics_key():
    class Test(CommandMetrics):
        command_metrics_key = 'MyTestCommandMetrics'
        pass

    commandmetrics = Test(None, 'command_group', None, properties,
                          event_notifier)
    assert commandmetrics.command_metrics_key == 'MyTestCommandMetrics'


def test_error_percentage():
    properties = get_unit_test_properties_setter()
    metrics = get_metrics(properties)

    metrics.mark_success(100)
    assert 0 == metrics.health_counts().error_percentage()

    metrics.mark_failure(1000)
    assert 50 == metrics.health_counts().error_percentage()

    metrics.mark_success(100)
    metrics.mark_success(100)
    assert 25 == metrics.health_counts().error_percentage()

    metrics.mark_timeout(5000)
    metrics.mark_timeout(5000)
    assert 50 == metrics.health_counts().error_percentage()

    metrics.mark_success(100)
    metrics.mark_success(100)
    metrics.mark_success(100)

    # latent
    metrics.mark_success(5000)

    # 6 success + 1 latent success + 1 failure + 2 timeout = 10 total
    # latent success not considered error
    # error percentage = 1 failure + 2 timeout / 10
    assert 30 == metrics.health_counts().error_percentage()


def test_bad_request_do_not_affect_error_percentage():
    properties = get_unit_test_properties_setter()
    metrics = get_metrics(properties)

    metrics.mark_success(100)
    assert 0 == metrics.health_counts().error_percentage()

    metrics.mark_failure(1000)
    assert 50 == metrics.health_counts().error_percentage()

    metrics.mark_bad_request(1)
    metrics.mark_bad_request(2)
    assert 50 == metrics.health_counts().error_percentage()

    metrics.mark_failure(45)
    metrics.mark_failure(55)
    assert 75 == metrics.health_counts().error_percentage()


"""
def test_current_concurrent_exection_count():
    class LatentCommand(Command):
        def __init__(self, duration):
            super().__init__(timeout=1000)
            self.duration = duration

        def run(self):
            time.sleep(self.duration)
            return True

        def fallback(self):
            return False

    metrics = None
    for _ in range(7):
        cmd = LatentCommand(400)
        if metrics is None:
            metrics = cmd.metrics
        cmd.queue()

    assert 8 == metrics.current_concurrent_execution_count()
"""


# TODO: Move this to utils.py file
# Utility method for creating :class:`hystrix.command_metrics.CommandMetrics`
# for unit tests.
def get_metrics(setter):
    return CommandMetrics('command_test', 'command_test', None,
                          as_mock(setter), EventNotifierDefault.get_instance())
