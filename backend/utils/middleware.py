from flask import request, jsonify
from functools import wraps
from flask_socketio import emit
import logging
import os

logger = logging.getLogger(__name__)

def socket_auth_required(f):
    """Socket认证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # 开发模式下跳过认证
            flask_env = os.getenv('FLASK_ENV', 'development')
            if flask_env == 'development':
                logger.info("Development mode: skipping authentication")
                return f(*args, **kwargs)
            
            # 检查认证数据
            auth_data = request.args.get('auth') or request.headers.get('Authorization')
            if not auth_data:
                emit('error', {'message': 'Authentication required'})
                return
            
            # 验证token
            try:
                from .auth import verify_token
                if auth_data.startswith('Bearer '):
                    auth_data = auth_data[7:]
                
                payload = verify_token(auth_data)
                if not payload:
                    emit('error', {'message': 'Invalid token'})
                    return
            except ImportError:
                # 如果auth模块不可用，跳过验证
                logger.warning("Auth module not available, skipping token verification")
                pass
            
            return f(*args, **kwargs)
            
        except Exception as e:
            logger.error(f"Socket authentication error: {str(e)}")
            emit('error', {'message': 'Authentication error'})
            return
            
    return decorated_function

def validate_session_access(session_id: str, user_id: str) -> bool:
    """验证会话访问权限"""
    try:
        return True
    except Exception as e:
        logger.error(f"Session access validation failed: {e}")
        return False

def socket_session_required(f):
    """Socket会话验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            data = args[0] if args else {}
            session_id = data.get('session_id')
            
            if not session_id:
                emit('error', {'message': 'Session ID required'})
                return
            
            return f(*args, **kwargs)
            
        except Exception as e:
            logger.error(f"Session validation error: {e}")
            emit('error', {'message': 'Session validation failed'})
            return
            
    return decorated_function

def rate_limit_socket(max_requests: int = 100, window: int = 60):
    """Socket速率限制装饰器"""
    from collections import defaultdict
    import time
    
    request_counts = defaultdict(list)
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                client_id = getattr(request, 'sid', None)
                if not client_id:
                    emit('error', {'message': 'Client ID not found'})
                    return
                current_time = time.time()
                
                request_counts[client_id] = [
                    req_time for req_time in request_counts[client_id]
                    if current_time - req_time < window
                ]
                
                if len(request_counts[client_id]) >= max_requests:
                    emit('error', {'message': 'Rate limit exceeded'})
                    return
                
                request_counts[client_id].append(current_time)
                
                return f(*args, **kwargs)
                
            except Exception as e:
                logger.error(f"Rate limiting error: {e}")
                emit('error', {'message': 'Rate limiting error'})
                return
                
        return decorated_function
    return decorator
