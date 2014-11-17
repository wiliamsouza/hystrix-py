from __future__ import absolute_import, unicode_literals
import logging

import six

from .group import Group

log = logging.getLogger(__name__)


class CommandMetaclass(type):

    __blacklist = ('Command', 'CommandMetaclass')

    def __new__(cls, name, bases, attrs):
        new_class = type.__new__(cls, name, bases, attrs)

        if name in cls.__blacklist:
            return new_class

        group_name = attrs.get('__groupname__', '{}Group'.format(name))
        NewGroup = type(group_name, (Group,), dict(__groupname__=group_name))
        setattr(new_class, 'group', NewGroup())
        setattr(new_class, 'group_name', group_name)

        return new_class


class Command(six.with_metaclass(CommandMetaclass, object)):

    __groupname__ = None

    def __init__(self, timeout=None):
        self.timeout = timeout

    def run(self):
        raise NotImplementedError('Subclasses must implement this method.')

    def fallback(self):
        raise NotImplementedError('Subclasses must implement this method.')

    def execute(self, timeout=None):
        timeout = timeout or self.timeout
        future = self.group.executor.submit(self.run)
        try:
            future.result(timeout)
        except Exception:
            log.exception('exception calling run for {}'.format(self))
            log.info('run raises {}'.format(future.exception))
            try:
                log.info('trying fallback for {}'.format(self))
                self.fallback()
            except Exception:
                log.exception('exception calling fallback for {}'.format(self))

    def observe(self):
        return self.group.executor.submit(self.run)

    def queue(self):
        return self.group.executor.submit(self.run)
