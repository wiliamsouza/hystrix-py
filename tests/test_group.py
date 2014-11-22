from hystrix.group import Group


def test_default_groupname():
    class Test(Group):
        pass

    group = Test()
    assert group.group_name == 'TestGroup'


def test_manual_groupname():
    class Test(Group):
        __group_name__ = 'MyTestGroup'
        pass

    group = Test()
    assert group.group_name == 'MyTestGroup'
