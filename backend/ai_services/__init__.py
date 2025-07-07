"""
AI Services package for AI Chat Backend

This package contains AI service integrations for various AI providers.
"""

import os
import requests
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

# 导入统一AI服务
from .unified_ai import unified_ai_service, get_unified_ai_response

def get_ai_response(data: Dict[str, Any]) -> str:
    """获取AI回复 - 使用统一AI服务"""
    try:
        # 使用统一AI服务
        return get_unified_ai_response(data)
    except Exception as e:
        logger.error(f"Unified AI service error: {str(e)}")
        # 备用回复
        message = data.get('message', '')
        return f"我理解您的问题：{message}。让我为您提供帮助。"

def get_ai_models_info() -> Dict[str, Any]:
    """获取AI模型信息"""
    try:
        return unified_ai_service.get_ai_models_info()
    except Exception as e:
        logger.error(f"Error getting AI models info: {str(e)}")
        return {
            'models': {},
            'total_models': 0,
            'description': 'AI服务暂时不可用'
        }

# 保留原有函数以兼容性
def get_step_star_response(message: str) -> str:
    """Step Star AI回复 - 兼容性函数"""
    return get_unified_ai_response({'message': message, 'ai_model': 'step_star'})

def get_deepseek_response(message: str) -> str:
    """DeepSeek AI回复 - 兼容性函数"""
    return get_unified_ai_response({'message': message, 'ai_model': 'deepseek'})

def get_minichat_response(message: str) -> str:
    """MiniChat AI回复 - 兼容性函数"""
    return get_unified_ai_response({'message': message, 'ai_model': 'minichat'})

# 导入基类
from .base import BaseAIService

# 导出所有函数和类
__all__ = [
    'get_ai_response',
    'get_ai_models_info',
    'get_step_star_response',
    'get_deepseek_response', 
    'get_minichat_response',
    'BaseAIService',
    'unified_ai_service'
]

__version__ = '2.0.0'
__author__ = 'AI Chat Team'
