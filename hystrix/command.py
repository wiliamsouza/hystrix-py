"""
Used to wrap code that will execute potentially risky functionality
(typically meaning a service call over the network) with fault and latency
tolerance, statistics and performance metrics capture, circuit breaker and
bulkhead functionality.
"""
from __future__ import absolute_import
import logging

import six

from hystrix.group import Group
from hystrix.command_metrics import CommandMetrics
from hystrix.command_properties import CommandProperties

log = logging.getLogger(__name__)


# TODO: Change this to an AbstractCommandMetaclass
class CommandMetaclass(type):

    __blacklist__ = ('Command', 'CommandMetaclass')

    def __new__(cls, name, bases, attrs):
        # Command key initialization
        command_key = attrs.get('command_key') or name
        new_class = type.__new__(cls, command_key, bases, attrs)

        if name in cls.__blacklist__:
            return new_class

        # TODO: Check instance CommandProperties here?
        command_properties_defaults = attrs.get('command_properties_defaults')
        if command_properties_defaults is None:
            command_properties_defaults = CommandProperties.setter()

        # Properties initialization
        properties_strategy = attrs.get('properties_strategy')
        if properties_strategy is None:
            properties = CommandProperties(command_key,
                                           command_properties_defaults)

        # TODO: Check instance CommandProperties here?
        setattr(new_class, 'properties', properties)

        # Pool key
        # This defines which pool this command should run on.
        # It uses the pool_key if provided, then defaults to use Group key.
        # It can then be overridden by a property if defined so it can be
        # changed at runtime.
        pool_key = attrs.get('pool_key')

        # Group key initialization
        group_key = attrs.get('group_key') or '{}Group'.format(command_key)
        NewGroup = type(group_key, (Group,),
                        dict(group_key=group_key, pool_key=pool_key))

        setattr(new_class, 'group', NewGroup())
        setattr(new_class, 'group_key', group_key)
        setattr(new_class, 'command_key', command_key)

        # Metrics initialization
        command_metrics_key = '{}CommandMetrics'.format(command_key)
        # TODO: Check instance CommandMetrics here?
        metrics = attrs.get('metrics')
        if metrics is None:
            NewCommandMetrics = type(
                command_metrics_key, (CommandMetrics,),
                dict(command_metrics_key=command_metrics_key,
                     group_key=group_key, pool_key=pool_key))
            metrics = NewCommandMetrics(properties=properties)

        setattr(new_class, 'metrics', metrics)

        return new_class


# TODO: Change this to inherit from an AbstractCommand
class Command(six.with_metaclass(CommandMetaclass, object)):

    command_key = None
    group_key = None

    def __init__(self, group_key=None, command_key=None,
                 pool_key=None, circuit_breaker=None, pool=None,
                 command_properties_defaults=None,
                 pool_properties_defaults=None, metrics=None,
                 fallback_semaphore=None, execution_semaphore=None,
                 properties_strategy=None, execution_hook=None, timeout=None):
        self.timeout = timeout

    def run(self):
        raise NotImplementedError('Subclasses must implement this method.')

    def fallback(self):
        raise NotImplementedError('Subclasses must implement this method.')

    def cache(self):
        raise NotImplementedError('Subclasses must implement this method.')

    def execute(self, timeout=None):
        timeout = timeout or self.timeout
        future = self.group.pool.submit(self.run)
        try:
            return future.result(timeout)
        except Exception:
            log.exception('exception calling run for {}'.format(self))
            log.info('run raises {}'.format(future.exception))
            try:
                log.info('trying fallback for {}'.format(self))
                future = self.group.pool.submit(self.fallback)
                return future.result(timeout)
            except Exception:
                log.exception('exception calling fallback for {}'.format(self))
                log.info('run() raised {}'.format(future.exception))
                log.info('trying cache for {}'.format(self))
                future = self.group.pool.submit(self.cache)
                return future.result(timeout)

    def observe(self, timeout=None):
        timeout = timeout or self.timeout
        return self.__async(timeout=timeout)

    def queue(self, timeout=None):
        timeout = timeout or self.timeout
        return self.__async(timeout=timeout)

    def __async(self, timeout=None):
        timeout = timeout or self.timeout
        future = self.group.pool.submit(self.run)
        try:
            # Call result() to check for exception
            future.result(timeout)
            return future
        except Exception:
            log.exception('exception calling run for {}'.format(self))
            log.info('run raised {}'.format(future.exception))
            try:
                log.info('trying fallback for {}'.format(self))
                future = self.group.pool.submit(self.fallback)
                # Call result() to check for exception
                future.result(timeout)
                return future
            except Exception:
                log.exception('exception calling fallback for {}'.format(self))
                log.info('fallback raised {}'.format(future.exception))
                log.info('trying cache for {}'.format(self))
                return self.group.pool.submit(self.cache)
