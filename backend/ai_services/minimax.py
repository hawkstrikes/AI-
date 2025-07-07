import os
import logging
import requests
import time
import socket
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

def load_env_file(env_file_path):
    if os.path.exists(env_file_path):
        with open(env_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

# 自动加载 config.env
current_dir = os.path.dirname(os.path.abspath(__file__))
load_env_file(os.path.join(current_dir, '../config.env'))
load_env_file(os.path.join(current_dir, 'config.env'))

class MinimaxAI:
    def __init__(self, api_key, group_id=None):
        self.api_key = api_key
        self.group_id = group_id
        self.base_url = "https://api.minimax.chat/v1/text/chatcompletion_v2"
        self.conversation_history = []

    def generate_response(self, prompt, user_id="用户", system_prompt="MiniMax AI"):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 构建消息历史
        messages = []
        
        # 添加系统消息
        messages.append({
            "role": "system",
            "content": system_prompt
        })
        
        # 添加对话历史
        if self.conversation_history:
            messages.extend(self.conversation_history)
        
        # 添加当前用户消息
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        payload = {
            "model": "MiniMax-Text-01",
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2048
        }
        
        # 如果有group_id，添加到headers中
        if self.group_id:
            headers["Group-Id"] = self.group_id
        
        try:
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=30)
            if response.status_code == 200:
                data = response.json()
                ai_response = data["choices"][0]["message"]["content"]
                
                # 更新对话历史
                self.conversation_history.append({"role": "user", "content": prompt})
                self.conversation_history.append({"role": "assistant", "content": ai_response})
                
                # 保持对话历史在合理长度内
                if len(self.conversation_history) > 10:
                    self.conversation_history = self.conversation_history[-10:]
                
                return ai_response
            else:
                logger.error(f"MiniMax API error: {response.status_code} - {response.text}")
                return f"抱歉，MiniMax AI暂时无法回复，请稍后重试。错误信息：{response.text}"
        except Exception as e:
            logger.error(f"MiniMax API exception: {e}")
            return f"抱歉，MiniMax AI暂时无法回复，请稍后重试。错误信息：{e}"

    def clear_history(self):
        """清空对话历史"""
        self.conversation_history = []

def generate_response(data):
    """MiniMax AI服务响应生成函数"""
    try:
        api_key = os.getenv('MINIMAX_API_KEY')
        group_id = os.getenv('MINIMAX_GROUP_ID')
        
        if not api_key:
            raise Exception("MINIMAX_API_KEY is required")
        
        service = MinimaxAI(api_key, group_id)
        return service.generate_response(
            prompt=data.get('message', ''),
            user_id=data.get('user_id', '用户'),
            system_prompt=data.get('system_prompt', 'MiniMax AI')
        )
    except Exception as e:
        logger.error(f"MiniMax service error: {e}")
        return f"MiniMax服务错误: {str(e)}"

if __name__ == "__main__":
    api_key = os.getenv('MINIMAX_API_KEY')
    group_id = os.getenv('MINIMAX_GROUP_ID')
    if not api_key:
        print("[测试] MINIMAX_API_KEY 未配置，无法测试。")
    else:
        ai = MinimaxAI(api_key, group_id)
        print("[测试] MiniMaxAI.generate_response('你好，MiniMax！') => ")
        result = ai.generate_response("你好，MiniMax！")
        print(result) 