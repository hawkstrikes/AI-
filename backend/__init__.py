"""
AI Chat Backend Package

A Flask-based backend for multi-AI chat system with WebSocket support.
"""

__version__ = '1.0.0'
__author__ = 'AI Chat Team'
__description__ = 'Multi-AI Chat Backend with Flask, SocketIO, and SQLAlchemy'

# 导入主要模块
from . import app
from . import models
from . import utils
from . import ai_services

__all__ = [
    'app',
    'models',
    'utils', 
    'ai_services'
] 