import os
import logging
import requests
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class ClaudeService:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.anthropic.com/v1"
        self.conversation_history = []
        
    def generate_response(self, prompt: str, user_id: str = 'user1', personality: Optional[Dict] = None) -> str:
        """生成Claude回复"""
        try:
            # 构建消息历史
            messages = []
            
            # 添加对话历史
            if self.conversation_history:
                messages.extend(self.conversation_history)
            
            # 添加当前用户消息
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            # 构建请求体
            request_body = {
                "model": "claude-3-sonnet-20240229",
                "max_tokens": 2048,
                "messages": messages,
                "system": "你是Anthropic提供的Claude AI助手，擅长中文、英文等多种语言的对话。请提供准确、有用的回答。"
            }
            
            # 发送请求
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }
            
            response = requests.post(
                f"{self.base_url}/messages",
                headers=headers,
                json=request_body,
                timeout=30
            )
            
            if response.status_code == 200:
                response_data = response.json()
                
                # 获取AI回复
                ai_response = response_data["content"][0]["text"]
                
                # 更新对话历史
                self.conversation_history.extend(response_data["content"])
                
                # 保持对话历史在合理长度内
                if len(self.conversation_history) > 20:
                    self.conversation_history = self.conversation_history[-20:]
                
                return ai_response
            else:
                raise Exception(f"API request failed with status {response.status_code}: {response.text}")
                
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            return f"抱歉，Claude暂时无法回复，请稍后重试。错误信息：{str(e)}"
    
    def clear_history(self):
        """清空对话历史"""
        self.conversation_history = []

def generate_response(data):
    """Claude服务响应生成函数"""
    try:
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise Exception("ANTHROPIC_API_KEY not configured")
        
        service = ClaudeService(api_key)
        return service.generate_response(
            prompt=data.get('message', ''),
            user_id=data.get('user_id', 'user1')
        )
    except Exception as e:
        logger.error(f"Claude service error: {e}")
        return f"Claude服务错误: {str(e)}"
