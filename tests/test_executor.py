from hystrix.executor import Executor


def test_default_executorname():
    class Test(Executor):
        pass

    executor = Test()
    assert executor.executor_name == 'TestExecutor'


def test_manual_executorname():
    class Test(Executor):
        __executorname__ = 'MyTestExecutor'
        pass

    executor = Test()
    assert executor.executor_name == 'MyTestExecutor'
