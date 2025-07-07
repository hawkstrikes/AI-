"""
通用装饰器，用于减少重复代码
"""

import logging
from functools import wraps
from typing import Callable, Any, Optional

logger = logging.getLogger(__name__)

def handle_exceptions(default_return: Any = None, log_error: bool = True):
    """通用异常处理装饰器"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_error:
                    logger.error(f"Error in {func.__name__}: {str(e)}")
                return default_return
        return wrapper
    return decorator

def validate_db_session(func: Callable) -> Callable:
    """验证数据库会话的装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        from .event_handlers import check_db_session
        if not check_db_session():
            return None
        return func(*args, **kwargs)
    return wrapper

def log_function_call(func: Callable) -> Callable:
    """记录函数调用的装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.debug(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
        result = func(*args, **kwargs)
        logger.debug(f"{func.__name__} returned: {result}")
        return result
    return wrapper

def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """失败重试装饰器"""
    import time
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {str(e)}")
                        time.sleep(delay)
                    else:
                        logger.error(f"All {max_retries} attempts failed for {func.__name__}: {str(e)}")
            
            if last_exception:
                raise last_exception
        return wrapper
    return decorator 