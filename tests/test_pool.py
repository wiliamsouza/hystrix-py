from hystrix.pool import Pool


def test_default_executorname():
    class Test(Pool):
        pass

    executor = Test()
    assert executor.pool_key == 'TestPool'


def test_manual_executorname():
    class Test(Pool):
        pool_key = 'MyTestPool'
        pass

    executor = Test()
    assert executor.pool_key == 'MyTestPool'
