from hystrix.pool_metrics import PoolMetrics


def test_default_pool_metrics_name():
    class Test(PoolMetrics):
        pass

    poolmetrics = Test()
    assert poolmetrics.pool_metrics_key == 'TestPoolMetrics'


def test_manual_pool_metrics_name():
    class Test(PoolMetrics):
        pool_metrics_key = 'MyTestPoolMetrics'
        pass

    poolmetrics = Test()
    assert poolmetrics.pool_metrics_key == 'MyTestPoolMetrics'
