from hystrix.metrics import CommandMetrics, ExecutorMetrics


def test_default_command_metrics_name():
    class Test(CommandMetrics):
        pass

    commandmetrics = Test()
    assert commandmetrics.command_metrics_name == 'TestCommandMetrics'


def test_manual_command_metrics_name():
    class Test(CommandMetrics):
        __command_metrics_name__ = 'MyTestCommandMetrics'
        pass

    commandmetrics = Test()
    assert commandmetrics.command_metrics_name == 'MyTestCommandMetrics'


def test_default_executor_metrics_name():
    class Test(ExecutorMetrics):
        pass

    executormetrics = Test()
    assert executormetrics.executor_metrics_name == 'TestExecutorMetrics'


def test_manual_executor_metrics_name():
    class Test(ExecutorMetrics):
        __executor_metrics_name__ = 'MyTestExecutorMetrics'
        pass

    executormetrics = Test()
    assert executormetrics.executor_metrics_name == 'MyTestExecutorMetrics'
