from hystrix.pool import Pool


def test_default_poolname():
    class Test(Pool):
        pass

    pool = Test()
    assert pool.pool_key == 'TestPool'


def test_manual_poolname():
    class Test(Pool):
        pool_key = 'MyTestPool'
        pass

    pool = Test()
    assert pool.pool_key == 'MyTestPool'
