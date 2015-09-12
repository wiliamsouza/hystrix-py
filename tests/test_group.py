from hystrix.group import Group


def test_default_groupname():
    class Test(Group):
        pass

    group = Test()
    assert group.group_key == 'TestGroup'


def test_manual_groupname():
    class Test(Group):
        group_key = 'MyTestGroup'
        pass

    group = Test()
    assert group.group_key == 'MyTestGroup'
