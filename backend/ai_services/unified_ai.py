"""
统一AI服务 - 整合多个AI模型形成多样性聊天效果
"""

import os
import random
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

# 导入具体的AI服务
from .deepseek import DeepSeekAI
from .minimax import MinimaxAI
from .stepchat import StepChatAI

logger = logging.getLogger(__name__)

def load_env_file(file_path):
    """加载环境变量文件"""
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

class UnifiedAIService:
    """统一AI服务 - 整合多个AI模型"""
    
    def __init__(self):
        # 主动加载环境变量
        self._load_environment()
        
        self.ai_models = {
            'deepseek': {
                'name': 'DeepSeek',
                'description': '深度思考型AI，擅长逻辑分析和复杂推理',
                'personality': '严谨、理性、善于分析',
                'style': 'formal',
                'temperature': 0.7
            },
            'minimax': {
                'name': 'MiniMax', 
                'description': '友好对话型AI，擅长日常交流和情感表达',
                'personality': '友好、幽默、善于倾听',
                'style': 'casual',
                'temperature': 0.8
            },
            'stepchat': {
                'name': 'StepChat',
                'description': '创意灵感型AI，擅长创新思维和艺术表达',
                'personality': '创意、开放、富有想象力',
                'style': 'creative',
                'temperature': 0.9
            }
        }
        
        # 初始化AI服务实例
        self.ai_services = {}
        self._init_ai_services()
        
        # 对话历史记录
        self.conversation_history = {}
        
        # 用户偏好分析
        self.user_preferences = {}
        
        # 模拟模式标志
        self.simulation_mode = False
        
    def _load_environment(self):
        """加载环境变量"""
        try:
            # 获取当前文件所在目录
            current_dir = Path(__file__).parent.parent.parent.absolute()
            
            # 尝试加载不同的配置文件
            config_files = [
                current_dir / 'backend' / 'config.env',
                current_dir / '.env',
                current_dir / 'production.env'
            ]
            
            for config_file in config_files:
                if os.path.exists(config_file):
                    load_env_file(config_file)
                    logger.info(f"已加载环境变量文件: {config_file}")
                    break
                    
        except Exception as e:
            logger.error(f"加载环境变量失败: {e}")
        
    def _init_ai_services(self):
        """初始化AI服务实例"""
        try:
            # 检查是否有有效的API密钥
            deepseek_key = os.getenv('DEEPSEEK_API_KEY')
            minimax_key = os.getenv('MINIMAX_API_KEY')
            minimax_group_id = os.getenv('MINIMAX_GROUP_ID')
            stepchat_key = os.getenv('STEPCHAT_API_KEY')
            
            # 检查是否为测试密钥或空值
            test_keys = ['sk-1234567890abcdef', 'test_key', '', None]
            
            # 初始化DeepSeek
            if deepseek_key and deepseek_key not in test_keys:
                try:
                    self.ai_services['deepseek'] = DeepSeekAI(deepseek_key)
                    logger.info("DeepSeek AI服务初始化成功")
                except Exception as e:
                    logger.error(f"DeepSeek初始化失败: {e}")
            
            # 初始化MiniMax
            if minimax_key and minimax_group_id and minimax_key not in test_keys:
                try:
                    self.ai_services['minimax'] = MinimaxAI(minimax_key, minimax_group_id)
                    logger.info("MiniMax AI服务初始化成功")
                except Exception as e:
                    logger.error(f"MiniMax初始化失败: {e}")
            
            # 初始化StepChat
            if stepchat_key and stepchat_key not in test_keys:
                try:
                    self.ai_services['stepchat'] = StepChatAI(stepchat_key)
                    logger.info("StepChat AI服务初始化成功")
                except Exception as e:
                    logger.error(f"StepChat初始化失败: {e}")
            
            # 检查是否有可用的AI服务
            if not self.ai_services:
                logger.warning("没有可用的AI服务，启用模拟模式")
                self.simulation_mode = True
            else:
                logger.info(f"成功初始化 {len(self.ai_services)} 个AI服务")
                self.simulation_mode = False  # 有真实服务时禁用模拟模式
                
        except Exception as e:
            logger.error(f"AI服务初始化失败: {e}")
            self.simulation_mode = True
        
    def get_ai_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """获取AI回复 - 整合多个AI模型"""
        try:
            message = data.get('message', '')
            session_id = data.get('session_id', 'default')
            user_id = data.get('user_id', 'user')
            
            # 分析消息内容和上下文
            context = self._analyze_context(message, session_id)
            
            # 选择合适的AI模型组合
            selected_models = self._select_ai_models(context, user_id)
            
            # 生成多样性回复
            responses = self._generate_diverse_responses(message, selected_models, context)
            
            # 整合回复
            final_response = self._integrate_responses(responses, context)
            
            # 更新对话历史
            self._update_conversation_history(session_id, message, final_response, context)
            
            return {
                'response': final_response,
                'ai_models_used': selected_models,
                'context': context,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Unified AI service error: {str(e)}")
            return {
                'response': f"抱歉，我遇到了一些问题。让我重新思考一下：{data.get('message', '')}",
                'ai_models_used': ['fallback'],
                'context': {'error': str(e)},
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def _analyze_context(self, message: str, session_id: str) -> Dict[str, Any]:
        """分析消息上下文"""
        context = {
            'message_length': len(message),
            'sentiment': self._analyze_sentiment(message),
            'topic': self._detect_topic(message),
            'complexity': self._assess_complexity(message),
            'conversation_history': self.conversation_history.get(session_id, []),
            'time_of_day': datetime.now().hour
        }
        
        # 分析用户偏好
        if session_id in self.user_preferences:
            context['user_preferences'] = self.user_preferences[session_id]
        
        return context
    
    def _analyze_sentiment(self, message: str) -> str:
        """分析消息情感"""
        positive_words = ['好', '棒', '喜欢', '爱', '开心', '高兴', '满意', '优秀', '精彩', '谢谢', '感谢']
        negative_words = ['不好', '讨厌', '难过', '失望', '糟糕', '问题', '困难', '痛苦', '烦', '累']
        
        positive_count = sum(1 for word in positive_words if word in message)
        negative_count = sum(1 for word in negative_words if word in message)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'
    
    def _detect_topic(self, message: str) -> str:
        """检测消息主题"""
        topics = {
            'technology': ['技术', '编程', '代码', '软件', '硬件', '电脑', '手机', '互联网', 'AI', '人工智能'],
            'business': ['商业', '工作', '公司', '项目', '管理', '市场', '销售', '投资', '创业'],
            'education': ['学习', '教育', '学校', '课程', '知识', '考试', '老师', '学生', '培训'],
            'entertainment': ['娱乐', '游戏', '电影', '音乐', '艺术', '旅游', '美食', '运动', '笑话'],
            'personal': ['个人', '生活', '家庭', '朋友', '情感', '健康', '心情', '梦想', '未来']
        }
        
        for topic, keywords in topics.items():
            if any(keyword in message for keyword in keywords):
                return topic
        
        return 'general'
    
    def _assess_complexity(self, message: str) -> str:
        """评估消息复杂度"""
        if len(message) > 100 or any(char in message for char in ['？', '!', '。', '，']):
            return 'complex'
        elif len(message) > 50:
            return 'medium'
        else:
            return 'simple'
    
    def _select_ai_models(self, context: Dict[str, Any], user_id: str) -> List[str]:
        """选择合适的AI模型组合"""
        selected_models = []
        
        # 在模拟模式下，从所有可用模型中选择
        available_models = list(self.ai_models.keys()) if self.simulation_mode else list(self.ai_services.keys())
        
        # 基于消息复杂度选择
        if context['complexity'] == 'complex':
            if 'deepseek' in available_models:
                selected_models.append('deepseek')  # 复杂问题用DeepSeek
        
        # 基于情感选择
        if context['sentiment'] == 'positive':
            if 'minimax' in available_models:
                selected_models.append('minimax')  # 积极情感用MiniMax
        elif context['sentiment'] == 'negative':
            if 'stepchat' in available_models:
                selected_models.append('stepchat')  # 消极情感用StepChat提供创意解决方案
        
        # 基于主题选择
        if context['topic'] == 'technology':
            if 'deepseek' in available_models:
                selected_models.append('deepseek')
        elif context['topic'] == 'entertainment':
            if 'stepchat' in available_models:
                selected_models.append('stepchat')
        
        # 确保至少有一个模型
        if not selected_models:
            # 按优先级选择
            if 'minimax' in available_models:
                selected_models.append('minimax')
            elif 'deepseek' in available_models:
                selected_models.append('deepseek')
            elif 'stepchat' in available_models:
                selected_models.append('stepchat')
        
        # 随机添加第二个模型以增加多样性
        if len(selected_models) == 1 and random.random() < 0.3:
            remaining_models = [m for m in available_models if m not in selected_models]
            if remaining_models:
                selected_models.append(random.choice(remaining_models))
        
        return selected_models
    
    def _generate_diverse_responses(self, message: str, selected_models: List[str], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成多样性回复"""
        responses = []
        
        for model_name in selected_models:
            try:
                model_info = self.ai_models[model_name]
                
                # 根据模型特性调整消息
                adjusted_message = self._adjust_message_for_model(message, model_info, context)
                
                # 生成回复
                response = self._generate_single_response(adjusted_message, model_name, context)
                
                responses.append({
                    'model': model_name,
                    'response': response,
                    'personality': model_info['personality'],
                    'style': model_info['style']
                })
                
            except Exception as e:
                logger.error(f"Error generating response for {model_name}: {str(e)}")
                # 生成备用回复
                responses.append({
                    'model': model_name,
                    'response': f"[{model_info['name']}] 我理解您的问题：{message}",
                    'personality': model_info['personality'],
                    'style': model_info['style']
                })
        
        return responses
    
    def _adjust_message_for_model(self, message: str, model_info: Dict[str, Any], context: Dict[str, Any]) -> str:
        """根据模型特性调整消息"""
        if model_info['style'] == 'formal':
            # 为正式风格添加更多上下文
            return f"请以专业、严谨的方式回答：{message}"
        elif model_info['style'] == 'casual':
            # 为友好风格添加情感元素
            return f"请以友好、轻松的方式回答：{message}"
        elif model_info['style'] == 'creative':
            # 为创意风格添加创新元素
            return f"请以创新、富有想象力的方式回答：{message}"
        
        return message
    
    def _generate_single_response(self, message: str, model_name: str, context: Dict[str, Any]) -> str:
        """生成单个AI模型的回复"""
        try:
            if self.simulation_mode:
                # 模拟模式
                return self._generate_simulated_response(message, model_name)
            
            # 真实API调用
            if model_name in self.ai_services:
                service = self.ai_services[model_name]
                # 传递用户ID和消息
                response = service.generate_response(
                    prompt=message,
                    user_id=context.get('user_id', 'user1')
                )
                return response
            else:
                return self._generate_simulated_response(message, model_name)
                
        except Exception as e:
            logger.error(f"Error in {model_name} response generation: {str(e)}")
            return self._generate_simulated_response(message, model_name)
    
    def _generate_simulated_response(self, message: str, model_name: str) -> str:
        """生成模拟回复"""
        if model_name == 'deepseek':
            responses = [
                f"从技术角度来看，{message} 这个问题需要深入分析。",
                f"基于我的理解，{message} 涉及多个层面的考虑。",
                f"让我从逻辑角度分析一下：{message}",
                f"这个问题很有趣，{message} 让我为您详细解释。",
                f"从专业角度来说，{message} 需要综合考虑多个因素。",
                f"根据我的分析，{message} 可以从以下几个维度来理解。",
                f"从技术层面看，{message} 是一个值得深入研究的话题。"
            ]
        elif model_name == 'minimax':
            responses = [
                f"哈哈，{message} 这个问题很有意思呢！",
                f"我理解您的想法，{message} 确实值得讨论。",
                f"谢谢您分享这个想法，{message} 让我想想...",
                f"哇，{message} 这个想法很棒！",
                f"我完全理解您的感受，{message} 我们一起探讨一下吧！",
                f"这真是个有趣的问题，{message} 让我来帮您分析一下。",
                f"我很高兴您问这个问题，{message} 让我为您详细解答。"
            ]
        elif model_name == 'stepchat':
            responses = [
                f"✨ 关于 {message}，我有一个创意想法！",
                f"🌟 让我们用全新的视角来看待 {message}",
                f"💡 这让我想到了一个有趣的解决方案：{message}",
                f"🎨 从艺术的角度，{message} 可以这样理解...",
                f"🚀 让我们跳出常规思维，{message} 其实可以这样思考...",
                f"🌈 这是一个充满可能性的问题，{message} 让我为您展开想象！",
                f"🎭 从创意的角度看，{message} 有很多有趣的可能性。"
            ]
        else:
            responses = [f"AI回复：{message}"]
        
        return random.choice(responses)
    
    def _integrate_responses(self, responses: List[Dict[str, Any]], context: Dict[str, Any]) -> str:
        """整合多个AI的回复"""
        if len(responses) == 1:
            return responses[0]['response']
        
        # 整合多个回复
        integrated_parts = []
        
        for i, response in enumerate(responses):
            model_name = response['model']
            model_info = self.ai_models[model_name]
            
            # 添加模型标识
            if len(responses) > 1:
                integrated_parts.append(f"[{model_info['name']}] {response['response']}")
            else:
                integrated_parts.append(response['response'])
        
        # 根据回复数量选择整合方式
        if len(responses) == 2:
            # 两个回复：对话式整合
            return f"{integrated_parts[0]}\n\n{integrated_parts[1]}"
        else:
            # 多个回复：列表式整合
            return "\n\n".join(integrated_parts)
    
    def _update_conversation_history(self, session_id: str, user_message: str, ai_response: str, context: Dict[str, Any]):
        """更新对话历史"""
        if session_id not in self.conversation_history:
            self.conversation_history[session_id] = []
        
        self.conversation_history[session_id].append({
            'user_message': user_message,
            'ai_response': ai_response,
            'context': context,
            'timestamp': datetime.utcnow().isoformat()
        })
        
        # 保持历史记录在合理范围内
        if len(self.conversation_history[session_id]) > 50:
            self.conversation_history[session_id] = self.conversation_history[session_id][-25:]
    
    def get_ai_models_info(self) -> Dict[str, Any]:
        """获取AI模型信息"""
        return {
            'models': self.ai_models,
            'total_models': len(self.ai_models),
            'description': '统一AI服务整合了多个AI模型，提供多样化的聊天体验',
            'simulation_mode': self.simulation_mode,
            'available_services': list(self.ai_services.keys())
        }

# 全局实例
unified_ai_service = UnifiedAIService()

def get_unified_ai_response(data: Dict[str, Any]) -> str:
    """获取统一AI回复"""
    result = unified_ai_service.get_ai_response(data)
    return result['response'] 