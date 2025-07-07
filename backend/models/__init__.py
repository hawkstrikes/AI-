"""
Models package for AI Chat Backend

This package contains database models for chat messages and sessions.
"""

try:
    from sqlalchemy import create_engine, Column, String, Text, DateTime, Boolean, JSON, Integer
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker
except ImportError:
    # 如果SQLAlchemy未安装，提供友好的错误信息
    raise ImportError("SQLAlchemy is required. Please install it with: pip install sqlalchemy")

from datetime import datetime
import uuid

Base = declarative_base()

def generate_id():
    """生成唯一ID"""
    return str(uuid.uuid4())

class ChatMessage(Base):
    """聊天消息模型"""
    __tablename__ = 'chat_messages'
    
    id = Column(String(255), primary_key=True, default=generate_id)
    session_id = Column(String(255), nullable=False, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    content = Column(JSON, nullable=False)
    sender_type = Column(String(50), default='user')  # 'user' or 'ai'
    ai_service = Column(String(100))  # 使用的AI服务
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'user_id': self.user_id,
            'content': self.content,
            'sender_type': self.sender_type,
            'ai_service': self.ai_service,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

class ChatSession(Base):
    """聊天会话模型"""
    __tablename__ = 'chat_sessions'
    
    id = Column(String(255), primary_key=True, default=generate_id)
    creator_id = Column(String(255), nullable=False, index=True)
    ai_settings = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'creator_id': self.creator_id,
            'ai_settings': self.ai_settings,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# 导出所有模型
__all__ = [
    'Base',
    'ChatMessage',
    'ChatSession',
    'generate_id'
]

__version__ = '1.0.0'
__author__ = 'AI Chat Team'
