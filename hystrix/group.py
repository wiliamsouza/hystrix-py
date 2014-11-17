from __future__ import absolute_import, unicode_literals
import logging

import six

from .executor import Executor

log = logging.getLogger(__name__)


class GroupMetaclass(type):

    __groups = dict()
    __blacklist = ('Group', 'GroupMetaclass')

    def __new__(cls, name, bases, attrs):

        if name in cls.__blacklist:
            return super(GroupMetaclass, cls).__new__(cls, name, bases, attrs)

        classname = attrs.get('__groupname__', '{}Group'.format(name))
        new_class = super(GroupMetaclass, cls).__new__(cls, classname,
                                                       bases, attrs)

        exec_name = attrs.get('__executorname__',
                              '{}Executor'.format(classname))
        NewExecutor = type(exec_name, (Executor,),
                           dict(__executorname__=exec_name))
        setattr(new_class, 'executor', NewExecutor())
        setattr(new_class, 'executor_name', exec_name)
        setattr(new_class, 'group_name', classname)

        if classname not in cls.__groups:
            cls.__groups[classname] = new_class

        return cls.__groups[classname]


class Group(six.with_metaclass(GroupMetaclass, object)):

    __groupname__ = None
    __executorname__ = None
