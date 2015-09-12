from __future__ import absolute_import
import logging

import six

from .pool import Pool

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

        pool_key = attrs.get('poll_key') or '{}Pool'.format(group_key)
        NewPool = type(pool_key, (Pool,),
                       dict(pool_key=pool_key))

        setattr(new_class, 'pool', NewPool())
        setattr(new_class, 'pool_key', pool_key)
        setattr(new_class, 'group_key', group_key)

        return cls.__instances__[class_name]


class Group(six.with_metaclass(GroupMetaclass, object)):

    group_key = None
    pool_key = None
