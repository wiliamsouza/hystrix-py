from __future__ import absolute_import
import logging

import six

from .executor import Executor

log = logging.getLogger(__name__)


class GroupMetaclass(type):

    __instances__ = dict()
    __blacklist__ = ('Group', 'GroupMetaclass')

    def __new__(cls, name, bases, attrs):

        if name in cls.__blacklist__:
            return super(GroupMetaclass, cls).__new__(cls, name, bases, attrs)

        class_name = attrs.get('__group_name__', '{}Group'.format(name))
        new_class = super(GroupMetaclass, cls).__new__(cls, class_name,
                                                       bases, attrs)

        exec_name = attrs.get('__executor_name__',
                              '{}Executor'.format(class_name))
        NewExecutor = type(exec_name, (Executor,),
                           dict(__executor_name__=exec_name))
        setattr(new_class, 'executor', NewExecutor())
        setattr(new_class, 'executor_name', exec_name)
        setattr(new_class, 'group_name', class_name)

        if class_name not in cls.__instances__:
            cls.__instances__[class_name] = new_class

        return cls.__instances__[class_name]


class Group(six.with_metaclass(GroupMetaclass, object)):

    __group_name__ = None
    __executor_name__ = None
