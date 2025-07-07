import os
import logging
from typing import Dict, Any

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s: %(message)s'
)

def get_database_config() -> Dict[str, Any]:
    """获取数据库配置"""
    return {
        'url': os.getenv('DATABASE_URL'),
        'echo': os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    }

def get_redis_config() -> Dict[str, Any]:
    """获取Redis配置"""
    return {
        'url': os.getenv('REDIS_URL'),
        'decode_responses': True
    }

def get_flask_config() -> Dict[str, Any]:
    """获取Flask配置"""
    return {
        'SECRET_KEY': os.getenv('SECRET_KEY', 'dev-secret-key'),
        'DEBUG': os.getenv('FLASK_DEBUG', 'True').lower() == 'true',
        'HOST': os.getenv('HOST', '0.0.0.0'),
        'PORT': int(os.getenv('PORT', 5000))
    }

def get_ai_config() -> Dict[str, Any]:
    """获取AI服务配置"""
    return {
        'minimax_api_key': os.getenv('MINIMAX_API_KEY'),
        'minimax_group_id': os.getenv('MINIMAX_GROUP_ID'),
        'deepseek_api_key': os.getenv('DEEPSEEK_API_KEY'),
        'stepchat_api_key': os.getenv('STEPCHAT_API_KEY'),
        'stepstar_api_key': os.getenv('STEPSTAR_API_KEY'),
        'minichat_api_key': os.getenv('MINICHAT_API_KEY')
    }
