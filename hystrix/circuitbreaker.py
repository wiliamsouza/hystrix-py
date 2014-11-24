from __future__ import absolute_import
import logging

import six

log = logging.getLogger(__name__)


class CircuitBreakerMetaclass(type):

    __instances__ = dict()
    __blacklist__ = ('CircuitBreaker', 'CircuitBreakerMetaclass')

    def __new__(cls, name, bases, attrs):
        if name in cls.__blacklist__:
            return super(CircuitBreakerMetaclass, cls).__new__(cls, name,
                                                               bases, attrs)

        class_name = attrs.get('__circuit_breaker_name__',
                               '{}CircuitBreaker'.format(name))
        new_class = super(CircuitBreakerMetaclass, cls).__new__(cls,
                                                                class_name,
                                                                bases, attrs)

        setattr(new_class, 'circuit_breaker_name', class_name)

        if class_name not in cls.__instances__:
            cls.__instances__[class_name] = new_class

        return cls.__instances__[class_name]


class CircuitBreaker(six.with_metaclass(CircuitBreakerMetaclass, object)):

    __circuit_breaker_name__ = None
