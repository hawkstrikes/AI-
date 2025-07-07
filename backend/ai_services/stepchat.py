import os
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class StepChatAI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.conversation_history = []
        
    def generate_response(self, prompt: str, user_id: str = 'user1', personality: Optional[Dict] = None) -> str:
        """生成阶跃星辰AI回复"""
        try:
            # 构建消息历史
            messages = []
            
            # 添加系统消息
            messages.append({
                "role": "system",
                "content": "你是由阶跃星辰提供的AI聊天助手，你擅长中文，英文，以及多种其他语言的对话。在保证用户数据安全的前提下，你能对用户的问题和请求，作出快速和精准的回答。同时，你的回答和建议应该拒绝黄赌毒，暴力恐怖主义的内容"
            })
            
            # 添加对话历史
            if self.conversation_history:
                messages.extend(self.conversation_history)
            
            # 添加当前用户消息
            messages.append({
                "role": "user",
                "content": prompt
            })
            
            # 调用API
            raise NotImplementedError("StepChatAI 目前未实现 API 调用逻辑，请补充实现。")
            
            # 获取回复
            ai_response = completion.choices[0].message.content
            
            # 更新对话历史
            self.conversation_history.append({"role": "user", "content": prompt})
            self.conversation_history.append({"role": "assistant", "content": ai_response})
            
            # 保持对话历史在合理长度内
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]
            
            return ai_response
            
        except Exception as e:
            logger.error(f"StepChat API error: {e}")
            return f"抱歉，阶跃星辰AI暂时无法回复，请稍后重试。错误信息：{str(e)}"
    
    def clear_history(self):
        """清空对话历史"""
        self.conversation_history = []

def generate_response(data):
    """阶跃星辰AI服务响应生成函数"""
    try:
        api_key = os.getenv('STEPCHAT_API_KEY')
        if not api_key:
            raise Exception("STEPCHAT_API_KEY not configured")
        
        service = StepChatAI(api_key)
        return service.generate_response(
            prompt=data.get('message', ''),
            user_id=data.get('user_id', 'user1')
        )
    except Exception as e:
        logger.error(f"StepChat service error: {e}")
        return f"阶跃星辰服务错误: {str(e)}" 