from hystrix.command_metrics import CommandMetrics
from hystrix.command_properties import CommandProperties

setter = CommandProperties.setter()
properties = CommandProperties('TEST', setter, 'unit_test_prefix')


def test_default_command_metrics_name():
    class Test(CommandMetrics):
        pass

    commandmetrics = Test('command_name', 'command_group', properties, 'event_notifier')
    assert commandmetrics.command_metrics_name == 'TestCommandMetrics'


def test_manual_command_metrics_name():
    class Test(CommandMetrics):
        __command_metrics_name__ = 'MyTestCommandMetrics'
        pass

    commandmetrics = Test('command_name', 'command_group', properties, 'event_notifier')
    assert commandmetrics.command_metrics_name == 'MyTestCommandMetrics'
