# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging

from .command_metrics import CommandMetrics
from .pool_metrics import PoolMetrics
from .pool import Pool
from .command import Command
from .group import Group


try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):

        def emit(self, record):
            pass

logging.getLogger('hystrix').addHandler(NullHandler())
