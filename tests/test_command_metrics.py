from hystrix.command_metrics import CommandMetrics
from hystrix.command_properties import CommandProperties
from hystrix.strategy.eventnotifier.event_notifier_default import EventNotifierDefault

from .test_command_properties import get_unit_test_properties_setter, as_mock

setter = CommandProperties.setter()
properties = CommandProperties('TEST', setter, 'unit_test_prefix')
event_notifier = EventNotifierDefault.get_instance()


def test_default_command_metrics_name():
    class Test(CommandMetrics):
        pass

    commandmetrics = Test('command_name', 'command_group', properties, event_notifier)
    assert commandmetrics.command_metrics_name == 'TestCommandMetrics'


def test_manual_command_metrics_name():
    class Test(CommandMetrics):
        __command_metrics_name__ = 'MyTestCommandMetrics'
        pass

    commandmetrics = Test('command_name', 'command_group', properties, event_notifier)
    assert commandmetrics.command_metrics_name == 'MyTestCommandMetrics'


# Disabled it
def error_percentage():
    properties = get_unit_test_properties_setter()
    metrics = get_metrics(properties)

    metrics.mark_success(100)
    assert 0 == metrics.health_counts().error_percentage()

    metrics.markFailure(1000)
    assert 50 == metrics.health_counts().error_percentage()

    metrics.mark_success(100)
    metrics.mark_success(100)
    assert 25 == metrics.health_counts().error_percentage()

    metrics.markTimeout(5000)
    metrics.markTimeout(5000)
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


# Utility method for creating :class:`hystrix.command_metrics.CommandMetrics` for unit tests.
# TODO: Move this to utils.py file
def get_metrics(setter):
    return CommandMetrics('command_name', 'command_group', as_mock(setter), EventNotifierDefault.get_instance())
