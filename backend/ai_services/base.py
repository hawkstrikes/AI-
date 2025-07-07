"""
AI服务基类，用于减少重复代码
"""

import os
import requests
from typing import Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)

class BaseAIService:
    """AI服务基类"""
    
    def __init__(self, api_key: str, base_url: str, service_name: str):
        self.api_key = api_key
        self.base_url = base_url
        self.service_name = service_name
    
    def _make_request(self, endpoint: str, payload: Dict[str, Any]) -> str:
        """发送API请求"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}{endpoint}",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return self._parse_response(response.json())
            else:
                raise Exception(f"{self.service_name} API Error: {response.text}")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"{self.service_name} request failed: {e}")
            raise Exception(f"{self.service_name} request failed: {str(e)}")
    
    def _parse_response(self, response_data: Dict[str, Any]) -> str:
        """解析API响应，子类可以重写此方法"""
        return str(response_data)
    
    def generate_response(self, prompt: str, **kwargs) -> str:
        """生成回复，子类必须实现此方法"""
        raise NotImplementedError("Subclasses must implement generate_response")

def get_api_key(env_var: str, service_name: str) -> str:
    """获取API密钥"""
    api_key = os.getenv(env_var)
    if not api_key:
        raise Exception(f"{service_name} API key not configured")
    return api_key

def create_service_response(data: Dict[str, Any], service_class, env_var: str, **kwargs) -> str:
    """创建服务响应的通用函数"""
    try:
        api_key = get_api_key(env_var, service_class.__name__)
        service = service_class(api_key, **kwargs)
        return service.generate_response(
            prompt=data.get('message', ''),
            **data
        )
    except Exception as e:
        logger.error(f"{service_class.__name__} error: {str(e)}")
        return f"{service_class.__name__} error: {str(e)}" 