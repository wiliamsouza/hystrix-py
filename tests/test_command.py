from hystrix.command import Command


class HelloCommand(Command):
    def run(self):
        return 'Hello Test'


class FailureCommand(Command):
    def run(self):
        raise RuntimeError('This command always fails')
        return 'Hello Test'

    def fallback(self):
        return 'Hello World'


def test_default_groupname():
    class TestCommand(Command):
        pass

    command = TestCommand()
    assert command.group_name == 'TestCommandGroup'


def test_manual_groupname():
    class TestCommand(Command):
        __groupname__ = 'MyTestGroup'
        pass

    command = TestCommand()
    assert command.group_name == 'MyTestGroup'
