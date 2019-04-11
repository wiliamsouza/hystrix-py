from hystrix.command import Command

import pytest


class HelloCommand(Command):
    def run(self):
        return 'Hello Run'


class FallbackCommand(Command):
    def run(self):
        raise RuntimeError('This command always fails')

    def fallback(self):
        return 'Hello Fallback'


class CacheCommand(Command):
    def run(self):
        raise RuntimeError('This command always fails')

    def fallback(self):
        raise RuntimeError('This command always fails')

    def cache(self):
        return 'Hello Cache'


def test_not_implemented_error():
    class NotImplementedCommand(Command):
        pass

    command = NotImplementedCommand()

    with pytest.raises(RuntimeError):
        command.run()

    with pytest.raises(RuntimeError):
        command.fallback()

    with pytest.raises(RuntimeError):
        command.cache()


def test_default_groupname():
    class RunCommand(Command):
        pass

    command = RunCommand()
    assert command.group_key == 'RunCommandGroup'


def test_manual_groupname():
    class RunCommand(Command):
        group_key = 'MyRunGroup'
        pass

    command = RunCommand()
    assert command.group_key == 'MyRunGroup'


def test_command_hello_synchronous():
    command = HelloCommand()
    result = command.execute()
    assert 'Hello Run' == result


def test_command_hello_asynchronous():
    command = HelloCommand()
    future = command.queue()
    assert 'Hello Run' == future.result()


def test_command_hello_callback():
    command = HelloCommand()
    future = command.observe()
    assert 'Hello Run' == future.result()


def test_command_hello_fallback_synchronous():
    command = FallbackCommand()
    result = command.execute()
    assert 'Hello Fallback' == result


def test_command_hello_fallback_asynchronous():
    command = FallbackCommand()
    future = command.queue()
    assert 'Hello Fallback' == future.result()


def test_command_hello_fallback_callback():
    command = FallbackCommand()
    future = command.observe()
    assert 'Hello Fallback' == future.result()


def test_command_hello_cache_synchronous():
    command = CacheCommand()
    result = command.execute()
    assert 'Hello Cache' == result


def test_command_hello_cache_asynchronous():
    command = CacheCommand()
    future = command.queue()
    assert 'Hello Cache' == future.result()


def test_command_hello_cache_callback():
    command = CacheCommand()
    future = command.observe()
    assert 'Hello Cache' == future.result()
