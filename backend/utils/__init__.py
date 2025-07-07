"""
Utils package for AI Chat Backend

This package contains utility modules for authentication, configuration,
middleware, and event handling.
"""

from . import auth
from . import config
from . import middleware
from . import event_handlers
from . import decorators

__all__ = [
    'auth',
    'config', 
    'middleware',
    'event_handlers',
    'decorators'
]

__version__ = '1.0.0'
__author__ = 'AI Chat Team' 