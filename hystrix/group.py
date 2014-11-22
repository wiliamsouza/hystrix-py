from __future__ import absolute_import
import logging

import six

from .executor import Executor

log = logging.getLogger(__name__)


class GroupMetaclass(type):

    __instances__ = dict()
    __blacklist = ('Group', 'GroupMetaclass')

    def __new__(cls, name, bases, attrs):

        if name in cls.__blacklist:
            return super(GroupMetaclass, cls).__new__(cls, name, bases, attrs)

        classname = attrs.get('__group_name__', '{}Group'.format(name))
        new_class = super(GroupMetaclass, cls).__new__(cls, classname,
                                                       bases, attrs)

        exec_name = attrs.get('__executor_name__',
                              '{}Executor'.format(classname))
        NewExecutor = type(exec_name, (Executor,),
                           dict(__executor_name__=exec_name))
        setattr(new_class, 'executor', NewExecutor())
        setattr(new_class, 'executor_name', exec_name)
        setattr(new_class, 'group_name', classname)

        if classname not in cls.__instances__:
            cls.__instances__[classname] = new_class

        return cls.__instances__[classname]


class Group(six.with_metaclass(GroupMetaclass, object)):

    __group_name__ = None
    __executor_name__ = None
