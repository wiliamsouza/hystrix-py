# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import logging

from .command import Command


try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):

        def emit(self, record):
            pass

logging.getLogger('hystrix').addHandler(NullHandler())
