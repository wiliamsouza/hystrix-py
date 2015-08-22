from atomos.multiprocessing.atomic import AtomicFloat


class MockedTime():

    def __init__(self):
        self._time = AtomicFloat(value=0)

    def current_time_in_millis(self):
        return self._time.get()

    def increment(self, millis):
        return self._time.add_and_get(millis)
