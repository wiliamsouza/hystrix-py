from hystrix.executor_metrics import ExecutorMetrics


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
