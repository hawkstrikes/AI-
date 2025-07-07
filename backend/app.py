# -*- coding: utf-8 -*-
"""
AI Chat Backend - 高性能优化版
支持用户认证、数据库存储、统一AI服务
"""

import os
import json
import logging
from datetime import datetime, timedelta
from functools import wraps
import traceback
import uuid
from sqlalchemy.exc import IntegrityError
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor
import time
import eventlet
import eventlet.wsgi

# 设置SQLAlchemy兼容性
os.environ['SQLALCHEMY_SILENCE_UBER_WARNING'] = '1'

# 加载环境变量
def load_env_file(env_file_path):
    """从.env文件加载环境变量"""
    if os.path.exists(env_file_path):
        with open(env_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

# 尝试加载环境变量文件
current_dir = os.path.dirname(os.path.abspath(__file__))
load_env_file(os.path.join(current_dir, 'config.env'))
load_env_file('config.env')
load_env_file('../config.env')
load_env_file('./config.env')
load_env_file(os.path.join(os.path.dirname(__file__), 'config.env'))

from flask import Flask, request, jsonify, session, g
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import jwt

# 导入AI服务（延迟导入，避免启动时阻塞）
def get_unified_ai_service():
    try:
        from ai_services.unified_ai import unified_ai_service
        return unified_ai_service
    except Exception as e:
        logger.error(f"AI服务导入失败: {e}")
        return None

# 延迟初始化AI服务
unified_ai_service = None

def ensure_ai_service():
    """确保AI服务已初始化"""
    global unified_ai_service
    if unified_ai_service is None:
        unified_ai_service = get_unified_ai_service()
    return unified_ai_service

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-2024')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_size': 20,
    'pool_recycle': 3600,
    'pool_pre_ping': True,
    'max_overflow': 30
}

# 性能优化配置
app.config['JSON_SORT_KEYS'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

# 初始化扩展
db = SQLAlchemy(app)
# 必须最早monkey_patch
eventlet.monkey_patch()
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet', ping_timeout=60, ping_interval=25)
CORS(app)

# 线程池执行器
executor = ThreadPoolExecutor(max_workers=10)

# 简单的内存缓存
class SimpleCache:
    def __init__(self):
        self.cache = {}
        self.lock = threading.Lock()
    
    def get(self, key):
        with self.lock:
            if key in self.cache:
                value, expire_time = self.cache[key]
                if expire_time > time.time():
                    return value
                else:
                    del self.cache[key]
            return None
    
    def set(self, key, value, ttl=300):  # 默认5分钟TTL
        with self.lock:
            self.cache[key] = (value, time.time() + ttl)
    
    def delete(self, key):
        with self.lock:
            if key in self.cache:
                del self.cache[key]

# 全局缓存实例
cache = SimpleCache()

# 数据模型
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # 关联聊天记录
    messages = db.relationship('ChatMessage', backref='user', lazy='dynamic')
    sessions = db.relationship('ChatSession', backref='user', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

class ChatSession(db.Model):
    __tablename__ = 'chat_sessions'
    
    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    ai_settings = db.Column(db.Text)  # JSON string of AI settings
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    title = db.Column(db.Text, default='')
    
    # 关联消息
    messages = db.relationship('ChatMessage', backref='session', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'ai_settings': json.loads(self.ai_settings) if self.ai_settings else {},
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'title': self.title or ''
        }

class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    session_id = db.Column(db.String(36), db.ForeignKey('chat_sessions.id'), nullable=False)
    message_type = db.Column(db.String(20), nullable=False)  # 'user' or 'ai'
    content = db.Column(db.Text, nullable=False)
    ai_models_used = db.Column(db.Text)  # JSON string of AI models
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'session_id': self.session_id,
            'type': self.message_type,
            'content': self.content,
            'ai_models_used': json.loads(self.ai_models_used) if self.ai_models_used else [],
            'timestamp': self.timestamp.isoformat()
        }

# JWT工具函数
def generate_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

def verify_token(token):
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

# 认证装饰器
def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or not token.startswith('Bearer '):
            return jsonify({'error': '缺少认证令牌'}), 401
        
        token = token.split(' ')[1]
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'error': '无效的认证令牌'}), 401
        
        # 获取用户信息
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': '用户不存在'}), 401
        
        g.current_user = user
        return f(*args, **kwargs)
    return decorated_function

# 异步AI响应生成
def generate_ai_response_async(data):
    """异步生成AI响应"""
    try:
        message = data.get('message', '')
        user_id = data.get('user_id')
        session_id = data.get('session_id')
        
        # 调用统一AI服务
        ai_service = ensure_ai_service()
        if ai_service is None:
            return {
                'response': '抱歉，AI服务暂时不可用，请稍后重试。',
                'ai_models_used': ['fallback']
            }
        
        ai_response_data = ai_service.get_ai_response({
            'message': message,
            'user_id': user_id,
            'session_id': session_id
        })
        
        return {
            'response': ai_response_data['response'],
            'ai_models_used': ai_response_data.get('ai_models_used', ['unified'])
        }
    except Exception as e:
        logger.error(f"AI响应生成失败: {e}")
        return {
            'response': '抱歉，我暂时无法回复，请稍后重试。',
            'ai_models_used': ['fallback']
        }

# 健康检查接口
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok"}), 200

# 用户注册接口
@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not all([username, email, password]):
            return jsonify({'error': '缺少必要参数'}), 400
        
        # 检查用户是否已存在
        if User.query.filter_by(username=username).first():
            return jsonify({'error': '用户名已存在'}), 400
        
        if User.query.filter_by(email=email).first():
            return jsonify({'error': '邮箱已存在'}), 400
        
        # 创建新用户
        password_hash = generate_password_hash(password)
        new_user = User(
            username=username,
            email=email,
            password_hash=password_hash
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        # 生成JWT令牌
        token = generate_token(new_user.id)
        
        return jsonify({
            'message': '注册成功',
            'token': token,
            'user': new_user.to_dict()
        }), 201
        
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': '用户已存在'}), 400
    except Exception as e:
        db.session.rollback()
        logger.error(f"注册失败: {e}")
        return jsonify({'error': '注册失败'}), 500

# 用户登录接口
@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not all([username, password]):
            return jsonify({'error': '缺少用户名或密码'}), 400
        
        # 查找用户
        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password_hash, password):
            return jsonify({'error': '用户名或密码错误'}), 401
        
        # 更新最后登录时间
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # 生成JWT令牌
        token = generate_token(user.id)
        
        return jsonify({
            'message': '登录成功',
            'token': token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"登录失败: {e}")
        return jsonify({'error': '登录失败'}), 500

# 验证认证接口
@app.route('/api/auth/verify', methods=['GET'])
@require_auth
def verify_auth():
    return jsonify({
        'message': '认证有效',
        'user': g.current_user.to_dict()
    }), 200

# 创建聊天会话
@app.route('/api/session/create', methods=['POST'])
@require_auth
def create_session():
    try:
        data = request.get_json()
        ai_settings = data.get('ai_settings', {})
        
        # 生成会话ID
        session_id = str(uuid.uuid4())
        
        # 创建新会话
        new_session = ChatSession(
            id=session_id,
            user_id=g.current_user.id,
            ai_settings=json.dumps(ai_settings)
        )
        
        db.session.add(new_session)
        db.session.commit()
        
        return jsonify({'session_id': new_session.id}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# 获取会话历史
@app.route('/api/session/<session_id>/history', methods=['GET'])
@require_auth
def get_session_history(session_id):
    try:
        # 验证会话所有权
        session_obj = ChatSession.query.filter_by(
            id=session_id, 
            user_id=g.current_user.id
        ).first()
        
        if not session_obj:
            return jsonify({'error': '会话不存在'}), 404
        
        # 获取消息历史
        messages = ChatMessage.query.filter_by(session_id=session_id)\
            .order_by(ChatMessage.timestamp.asc())\
            .all()
        
        return jsonify({
            'session': session_obj.to_dict(),
            'messages': [msg.to_dict() for msg in messages]
        }), 200
        
    except Exception as e:
        logger.error(f"获取会话历史失败: {e}")
        return jsonify({'error': '获取会话历史失败'}), 500

# 获取用户所有会话
@app.route('/api/sessions', methods=['GET'])
@require_auth
def get_user_sessions():
    try:
        sessions = ChatSession.query.filter_by(user_id=g.current_user.id)\
            .order_by(ChatSession.updated_at.desc())\
            .all()
        
        return jsonify({
            'sessions': [session.to_dict() for session in sessions]
        }), 200
        
    except Exception as e:
        logger.error(f"获取用户会话失败: {e}")
        return jsonify({'error': '获取用户会话失败'}), 500

# 删除会话
@app.route('/api/session/<session_id>', methods=['DELETE'])
@require_auth
def delete_session(session_id):
    try:
        # 验证会话所有权
        session_obj = ChatSession.query.filter_by(
            id=session_id, 
            user_id=g.current_user.id
        ).first()
        
        if not session_obj:
            return jsonify({'error': '会话不存在'}), 404
        
        # 删除会话及其消息
        ChatMessage.query.filter_by(session_id=session_id).delete()
        db.session.delete(session_obj)
        db.session.commit()
        
        return jsonify({'message': '会话删除成功'}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"删除会话失败: {e}")
        return jsonify({'error': '删除会话失败'}), 500

# 聊天接口
@app.route('/api/chat', methods=['POST'])
@require_auth
def chat():
    try:
        data = request.get_json()
        message = data.get('message')
        session_id = data.get('session_id')
        
        if not message:
            return jsonify({'error': '消息不能为空'}), 400
        
        if not session_id:
            return jsonify({'error': '缺少session_id'}), 400
        
        # 验证会话所有权
        session_obj = ChatSession.query.filter_by(
            id=session_id, 
            user_id=g.current_user.id
        ).first()
        
        if not session_obj:
            return jsonify({'error': '会话不存在'}), 404
        
        # 检查缓存
        cache_key = f"chat:{session_id}:{hash(message)}"
        cached_response = cache.get(cache_key)
        if cached_response:
            return jsonify(cached_response), 200
        
        # 保存用户消息
        user_message = ChatMessage(
            user_id=g.current_user.id,
            session_id=session_id,
            message_type='user',
            content=message
        )
        db.session.add(user_message)
        
        # 异步获取AI回复
        future = executor.submit(generate_ai_response_async, {
            'message': message,
            'user_id': g.current_user.id,
            'session_id': session_id
        })
        
        # 等待AI回复
        try:
            ai_response_data = future.result(timeout=30)
        except Exception as e:
            logger.error(f"AI响应超时: {e}")
            ai_response_data = {
                'response': '抱歉，我暂时无法回复，请稍后重试。',
                'ai_models_used': ['fallback']
            }
        
        # 保存AI回复
        ai_message = ChatMessage(
            user_id=g.current_user.id,
            session_id=session_id,
            message_type='ai',
            content=ai_response_data['response'],
            ai_models_used=json.dumps(ai_response_data.get('ai_models_used', ['unified']))
        )
        db.session.add(ai_message)
        
        # 更新会话时间
        session_obj.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # 缓存响应（短期缓存）
        response_data = {
            'response': ai_response_data['response'], 
            'ai_models_used': ai_response_data['ai_models_used'],
            'session_id': session_id
        }
        cache.set(cache_key, response_data, ttl=60)  # 1分钟缓存
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Chat error: {e}\n{traceback.format_exc()}")
        db.session.rollback()
        return jsonify({'error': '聊天失败'}), 500

@app.route('/api/chat/history/<int:user_id>', methods=['GET'])
@require_auth
def get_chat_history(user_id):
    try:
        # 验证用户只能访问自己的聊天记录
        if g.current_user.id != user_id:
            return jsonify({'error': '无权访问'}), 403
        
        # 检查缓存
        cache_key = f"chat_history:{user_id}"
        cached_history = cache.get(cache_key)
        if cached_history:
            return jsonify(cached_history), 200
        
        # 获取最近的50条消息
        messages = ChatMessage.query.filter_by(user_id=user_id)\
            .order_by(ChatMessage.timestamp.desc())\
            .limit(50)\
            .all()
        
        # 按时间正序排列
        messages.reverse()
        
        response_data = {
            'messages': [msg.to_dict() for msg in messages]
        }
        
        # 缓存历史记录（5分钟）
        cache.set(cache_key, response_data, ttl=300)
        
        return jsonify(response_data), 200
        
    except Exception as e:
        traceback.print_exc()
        logger.error(f"Get chat history error: {e}")
        return jsonify({'error': '获取聊天记录失败'}), 500

# AI模型信息API
@app.route('/api/ai/models', methods=['GET'])
def get_ai_models():
    try:
        # 检查缓存
        cache_key = "ai_models_info"
        cached_models = cache.get(cache_key)
        if cached_models:
            return jsonify(cached_models), 200
        
        ai_service = ensure_ai_service()
        if ai_service is None:
            models_info = {'error': 'AI服务未初始化'}
        else:
            models_info = ai_service.get_ai_models_info()
        
        # 缓存模型信息（10分钟）
        cache.set(cache_key, models_info, ttl=600)
        
        return jsonify(models_info), 200
    except Exception as e:
        logger.error(f"Get AI models error: {e}")
        return jsonify({'error': '获取AI模型信息失败'}), 500

# WebSocket事件处理
@socketio.on('connect')
def handle_connect():
    logger.info('Client connected')
    emit('status', {'message': 'Connected to AI Chat'})

@socketio.on('disconnect')
def handle_disconnect():
    logger.info('Client disconnected')

@socketio.on('send_message')
def handle_message(data):
    try:
        message = data.get('message')
        user_id = data.get('user_id')
        session_id = data.get('session_id')
        
        if not message:
            emit('error', {'message': '消息不能为空'})
            return
        
        if not session_id:
            emit('error', {'message': '缺少session_id'})
            return
        
        # 异步获取AI回复
        future = executor.submit(generate_ai_response_async, {
            'message': message,
            'user_id': user_id,
            'session_id': session_id
        })
        
        # 等待AI回复
        try:
            ai_response_data = future.result(timeout=30)
        except Exception as e:
            logger.error(f"WebSocket AI响应失败: {e}")
            ai_response_data = {
                'response': f"抱歉，我暂时无法回复，请稍后重试。",
                'ai_models_used': ['fallback']
            }
        
        # 发送AI回复
        emit('ai_response', {
            'response': ai_response_data['response'],
            'ai_models_used': ai_response_data.get('ai_models_used', ['unified']),
            'session_id': session_id
        })
        
    except Exception as e:
        logger.error(f"WebSocket message error: {e}")
        emit('error', {'message': '处理消息失败'})

# 错误处理
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': '接口不存在'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': '服务器内部错误'}), 500

# 数据库初始化函数
def init_database():
    """初始化数据库"""
    with app.app_context():
        try:
            db.create_all()
            logger.info("数据库表自动检查/修复完成")
        except Exception as e:
            logger.error(f"数据库自动修复失败: {e}")
            traceback.print_exc()

# 启动应用
if __name__ == '__main__':
    try:
        # 初始化数据库
        init_database()
        
        # 检查端口是否可用
        import socket
        port = 5000  # 后端使用5000端口
        
        # 尝试不同的端口
        for test_port in [5000, 5001, 5002, 8080, 8000, 3000]:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.bind(('localhost', test_port))
                sock.close()
                port = test_port
                break
            except OSError:
                continue
        
        print("Starting AI Chat Backend Service...")
        print(f"Service URL: http://localhost:{port}")
        print(f"Debug Mode: {app.config.get('FLASK_DEBUG', False)}")
        ai_service = ensure_ai_service()
        if ai_service is None:
            print("AI Services: 0 (未初始化)")
        else:
            print(f"AI Services: {len(ai_service.ai_services)}")
        
        # 使用eventlet启动
        eventlet.monkey_patch()
        
        # 启动服务
        socketio.run(
            app, 
            host='0.0.0.0', 
            port=port,
            debug=False,
            use_reloader=False,
            log_output=True,
            allow_unsafe_werkzeug=True
        )
        
    except Exception as e:
        print(f"Service startup failed: {e}")
        print("Possible solutions:")
        print("   1. Check if port is occupied")
        print("   2. Run with administrator privileges")
        print("   3. Check firewall settings")
        print("   4. Try different port")
        import traceback
        traceback.print_exc()
