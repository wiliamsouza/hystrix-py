# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging

from .metrics import CommandMetrics, ExecutorMetrics
from .executor import Executor
from .command import Command
from .group import Group


try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):

        def emit(self, record):
            pass

logging.getLogger('hystrix').addHandler(NullHandler())
