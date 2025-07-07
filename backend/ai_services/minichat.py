from typing import Optional, Dict, Any
from .base import BaseAIService, create_service_response

class MiniChatAI(BaseAIService):
    def __init__(self, api_key: str):
        super().__init__(api_key, "https://api.minichat.ai/v1", "MiniChat")
        
    def generate_response(self, prompt: str, voice_profile: Optional[Dict] = None) -> str:
        payload = {
            "input": prompt,
            "voice_id": voice_profile.get('id', 'default') if voice_profile else 'default',
            "voice_settings": voice_profile.get('settings', {}) if voice_profile else {}
        }
        
        return self._make_request("/chat", payload)
    
    def _parse_response(self, response_data: Dict[str, Any]) -> str:
        """解析MiniChat API响应"""
        return response_data['output']

def generate_response(data):
    """MiniChat AI服务响应生成函数"""
    return create_service_response(
        data=data,
        service_class=MiniChatAI,
        env_var='MINICHAT_API_KEY'
    ) 