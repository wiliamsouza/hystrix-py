from hystrix.circuitbreaker import CircuitBreaker


def test_default_circuitbreakername():
    class Test(CircuitBreaker):
        pass

    circuitbreaker = Test()
    assert circuitbreaker.circuit_breaker_name == 'TestCircuitBreaker'


def test_manual_circuitbreakername():
    class Test(CircuitBreaker):
        __circuit_breaker_name__ = 'MyTestCircuitBreaker'
        pass

    circuitbreaker = Test()
    assert circuitbreaker.circuit_breaker_name == 'MyTestCircuitBreaker'
