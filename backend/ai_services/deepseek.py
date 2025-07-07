from typing import Optional, Any, Dict
import os
import logging
import time
import requests

logger = logging.getLogger(__name__)

class DeepSeekAI:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def _test_connection(self) -> bool:
        """测试与DeepSeek API的连接"""
        try:
            # 测试基础连接
            response = requests.get(
                "https://api.deepseek.com/v1/models",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=10
            )
            logger.info(f"DeepSeek connection test status: {response.status_code}")
            return response.status_code == 200
        except requests.exceptions.Timeout:
            logger.error("DeepSeek connection test timeout")
            return False
        except requests.exceptions.ConnectionError:
            logger.error("DeepSeek connection test connection error")
            return False
        except Exception as e:
            logger.error(f"DeepSeek connection test failed: {e}")
            return False

    def generate_response(self, prompt: str, context: Optional[str] = None, user_id: str = 'user1') -> str:
        """生成DeepSeek AI回复（官方OpenAI兼容接口）"""
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                # 构建消息历史
                messages = []
                # 官方推荐的system prompt
                messages.append({
                    "role": "system",
                    "content": "You are a helpful assistant"
                })
                # 添加对话历史
                if self.conversation_history:
                    messages.extend(self.conversation_history)
                # 添加当前用户消息
                messages.append({
                    "role": "user",
                    "content": prompt
                })
                
                # 移除 self.client 相关API调用，改为 raise NotImplementedError 或 pass
                raise NotImplementedError("DeepSeekAI 目前未实现 API 调用逻辑，请补充实现。")
                
            except Exception as e:
                error_msg = str(e)
                logger.error(f"DeepSeek API error (attempt {attempt + 1}/{max_retries}): {error_msg}")
                
                # 检查是否是连接错误
                if "Connection" in error_msg or "timeout" in error_msg.lower():
                    if attempt < max_retries - 1:
                        logger.info(f"Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                        retry_delay *= 2  # 指数退避
                        continue
                    else:
                        # 最后一次尝试失败，测试连接
                        if not self._test_connection():
                            return "抱歉，DeepSeek AI暂时无法回复，请稍后重试。错误信息：网络连接异常，请检查网络设置。"
                        else:
                            return f"抱歉，DeepSeek AI暂时无法回复，请稍后重试。错误信息：Connection error (已重试{max_retries}次)"
                
                # 其他错误直接返回
                return f"抱歉，DeepSeek AI暂时无法回复，请稍后重试。错误信息：{error_msg}"
        
        return "抱歉，DeepSeek AI暂时无法回复，请稍后重试。错误信息：Connection error"

    def clear_history(self):
        """清空对话历史"""
        self.conversation_history = []

def generate_response(data):
    """DeepSeek AI服务响应生成函数"""
    try:
        api_key = os.getenv('DEEPSEEK_API_KEY')
        if not api_key:
            raise Exception("DEEPSEEK_API_KEY not configured")
        
        # 验证API密钥格式
        if not api_key.startswith('sk-'):
            raise Exception("Invalid API key format")
        
        service = DeepSeekAI(api_key)
        return service.generate_response(
            prompt=data.get('message', ''),
            user_id=data.get('user_id', 'user1')
        )
    except Exception as e:
        logger.error(f"DeepSeek service error: {e}")
        return f"DeepSeek服务错误: {str(e)}" 