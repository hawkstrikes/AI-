import os
import time
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')

def create_token(user_id: str, expires_in: int = 7 * 24 * 3600) -> str:
    """创建简单的token"""
    try:
        if not user_id:
            raise ValueError("User ID cannot be empty")
        
        timestamp = str(int(time.time()))
        token_data = f"{user_id}:{timestamp}:{SECRET_KEY}"
        token = hashlib.sha256(token_data.encode()).hexdigest()
        return f"{user_id}.{timestamp}.{token}"
    except Exception as e:
        logger.error(f"Token creation failed: {e}")
        raise

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """验证简单的token"""
    try:
        if not token:
            return None
        
        parts = token.split('.')
        if len(parts) != 3:
            return None
        
        user_id, timestamp, token_hash = parts
        
        # 验证token
        token_data = f"{user_id}:{timestamp}:{SECRET_KEY}"
        expected_hash = hashlib.sha256(token_data.encode()).hexdigest()
        
        if token_hash == expected_hash:
            # 检查是否过期（7天）
            token_time = int(timestamp)
            current_time = int(time.time())
            if current_time - token_time < 7 * 24 * 3600:  # 7天
                return {'sub': user_id, 'exp': token_time + 7 * 24 * 3600}
        
        return None
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        return None

def extract_user_id_from_token(token: str) -> Optional[str]:
    """从token中提取用户ID"""
    try:
        payload = verify_token(token)
        return payload.get('sub') if payload else None
    except Exception as e:
        logger.warning(f"Failed to extract user ID from token: {e}")
        return None

def create_user_session(user_id: str, session_data: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """创建用户会话"""
    try:
        if not user_id:
            logger.error("User ID cannot be empty")
            return None
        
        token = create_token(user_id)
        return {
            'user_id': user_id,
            'token': token,
            'expires_at': (datetime.utcnow() + timedelta(days=7)).isoformat(),
            'session_data': session_data or {}
        }
    except Exception as e:
        logger.error(f"Session creation failed: {e}")
        return None

def validate_user_session(token: str) -> Optional[Dict[str, Any]]:
    """验证用户会话"""
    try:
        payload = verify_token(token)
        if not payload:
            return None
        
        user_id = payload.get('sub')
        if not user_id:
            return None
        
        return {
            'user_id': user_id,
            'valid': True,
            'expires_at': datetime.fromtimestamp(payload['exp']).isoformat()
        }
    except Exception as e:
        logger.error(f"Session validation failed: {e}")
        return None

def refresh_user_token(token: str) -> Optional[Dict[str, Any]]:
    """刷新用户token"""
    try:
        payload = verify_token(token)
        if not payload:
            return None
        
        user_id = payload.get('sub')
        if not user_id:
            return None
        
        # 创建新token
        new_token = create_token(user_id)
        return {
            'user_id': user_id,
            'token': new_token,
            'expires_at': (datetime.utcnow() + timedelta(days=7)).isoformat()
        }
    except Exception as e:
        logger.error(f"Token refresh failed: {e}")
        return None

def validate_user_permission(user_id: str, resource_id: str, permission: str = 'read') -> bool:
    """验证用户权限（简化版本）"""
    try:
        if not user_id or not resource_id:
            return False
        return True
    except Exception as e:
        logger.error(f"Permission validation failed: {e}")
        return False

def get_token_expiration_time(token: str) -> Optional[datetime]:
    """获取token过期时间"""
    try:
        payload = verify_token(token)
        if payload and 'exp' in payload:
            return datetime.fromtimestamp(payload['exp'])
        return None
    except Exception as e:
        logger.error(f"Failed to get token expiration: {e}")
        return None

def is_token_expired(token: str) -> bool:
    """检查token是否过期"""
    try:
        payload = verify_token(token)
        return payload is None
    except Exception as e:
        logger.error(f"Failed to check token expiration: {e}")
        return True
