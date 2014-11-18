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

    def cache(self):
        raise NotImplementedError('Subclasses must implement this method.')

    def execute(self, timeout=None):
        timeout = timeout or self.timeout
        future = self.group.executor.submit(self.run)
        try:
            return future.result(timeout)
        except Exception:
            log.exception('exception calling run for {}'.format(self))
            log.info('run raises {}'.format(future.exception))
            try:
                log.info('trying fallback for {}'.format(self))
                future = self.group.executor.submit(self.fallback)
                return future.result(timeout)
            except Exception:
                log.exception('exception calling fallback for {}'.format(self))
                log.info('run() raised {}'.format(future.exception))
                log.info('trying cache for {}'.format(self))
                future = self.group.executor.submit(self.cache)
                return future.result(timeout)

    def observe(self, timeout=None):
        timeout = timeout or self.timeout
        return self.__async(timeout=timeout)

    def queue(self, timeout=None):
        timeout = timeout or self.timeout
        return self.__async(timeout=timeout)

    def __async(self, timeout=None):
        timeout = timeout or self.timeout
        future = self.group.executor.submit(self.run)
        try:
            # Call result() to check for exception
            future.result(timeout)
            return future
        except Exception:
            log.exception('exception calling run for {}'.format(self))
            log.info('run raised {}'.format(future.exception))
            try:
                log.info('trying fallback for {}'.format(self))
                future = self.group.executor.submit(self.fallback)
                # Call result() to check for exception
                future.result(timeout)
                return future
            except Exception:
                log.exception('exception calling fallback for {}'.format(self))
                log.info('fallback raised {}'.format(future.exception))
                log.info('trying cache for {}'.format(self))
                return self.group.executor.submit(self.cache)
