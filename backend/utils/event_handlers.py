import uuid
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError
from models import ChatMessage, ChatSession, Base

logger = logging.getLogger(__name__)

# 全局数据库会话 - 由app.py管理
db_session = None

def init_db(engine):
    """初始化数据库会话"""
    global db_session
    try:
        from sqlalchemy.orm import scoped_session, sessionmaker
        db_session = scoped_session(sessionmaker(bind=engine))
        logger.info("Database session initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Database session initialization failed: {e}")
        return False

def generate_message_id() -> str:
    """生成唯一的消息ID"""
    return str(uuid.uuid4())

def validate_session_id(session_id: str) -> bool:
    """验证会话ID"""
    if not session_id or not isinstance(session_id, str):
        logger.error("Invalid session_id")
        return False
    return True

def validate_user_id(user_id: str) -> bool:
    """验证用户ID"""
    if not user_id or not isinstance(user_id, str):
        logger.error("Invalid user_id")
        return False
    return True

def validate_content(content: Any) -> bool:
    """验证内容"""
    if content is None:
        logger.error("Content cannot be None")
        return False
    return True

def check_db_session() -> bool:
    """检查数据库会话是否可用"""
    if not db_session:
        logger.error("Database session not initialized")
        return False
    return True

def validate_inputs(session_id: str, user_id: str, content: Any) -> bool:
    """验证输入参数"""
    return (validate_session_id(session_id) and 
            validate_user_id(user_id) and 
            validate_content(content))

def save_message(session_id: str, user_id: str, content: Dict[str, Any], 
                sender_type: str = 'user', ai_service: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """保存消息到数据库"""
    if not validate_inputs(session_id, user_id, content):
        return None
    
    if not check_db_session():
        return None
    
    try:
        # 生成唯一消息ID
        message_id = generate_message_id()
        
        message = ChatMessage(
            id=message_id,
            session_id=session_id,
            user_id=user_id,
            content=content,
            sender_type=sender_type,
            ai_service=ai_service,
            timestamp=datetime.utcnow()
        )
        
        db_session.add(message)
        db_session.commit()
        
        logger.info(f"Message saved successfully: {message_id}")
        
        return {
            'id': message.id,
            'session_id': message.session_id,
            'user_id': message.user_id,
            'content': message.content,
            'sender_type': message.sender_type,
            'ai_service': message.ai_service,
            'timestamp': message.timestamp.isoformat()
        }
        
    except IntegrityError as e:
        logger.error(f"Integrity error saving message: {e}")
        db_session.rollback()
        return None
    except OperationalError as e:
        logger.error(f"Database operational error: {e}")
        db_session.rollback()
        return None
    except Exception as e:
        logger.error(f"Unexpected error saving message: {e}")
        db_session.rollback()
        return None

def get_session_history(session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    """获取会话历史消息"""
    if not validate_session_id(session_id):
        return []
    
    if not check_db_session():
        return []
    
    try:
        messages = db_session.query(ChatMessage)\
            .filter_by(session_id=session_id)\
            .order_by(ChatMessage.timestamp.desc())\
            .limit(limit)\
            .all()
        
        result = [{
            'id': msg.id,
            'session_id': msg.session_id,
            'user_id': msg.user_id,
            'content': msg.content,
            'sender_type': msg.sender_type,
            'ai_service': msg.ai_service,
            'timestamp': msg.timestamp.isoformat()
        } for msg in reversed(messages)]
        
        logger.info(f"Retrieved {len(result)} messages for session {session_id}")
        return result
        
    except OperationalError as e:
        logger.error(f"Database operational error getting history: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error getting session history: {e}")
        return []

def handle_user_join(session_id: str, user_id: str, is_creator: bool = False) -> Optional[Dict[str, Any]]:
    """处理用户加入会话"""
    if not validate_session_id(session_id) or not validate_user_id(user_id):
        return None
    
    if not check_db_session():
        return None
    
    try:
        # 检查会话是否存在
        session = db_session.query(ChatSession).filter_by(id=session_id).first()
        
        if not session:
            # 创建新会话
            session = ChatSession(
                id=session_id,
                creator_id=user_id,
                ai_settings={'service': 'step_star'},
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db_session.add(session)
            db_session.commit()
            logger.info(f"Created new session: {session_id}")
        else:
            # 更新会话的更新时间
            session.updated_at = datetime.utcnow()
            db_session.commit()
            logger.info(f"User {user_id} joined existing session: {session_id}")
        
        return {
            'id': session.id,
            'creator_id': session.creator_id,
            'ai_settings': session.ai_settings,
            'created_at': session.created_at.isoformat(),
            'updated_at': session.updated_at.isoformat()
        }
        
    except IntegrityError as e:
        logger.error(f"Integrity error handling user join: {e}")
        db_session.rollback()
        return None
    except OperationalError as e:
        logger.error(f"Database operational error: {e}")
        db_session.rollback()
        return None
    except Exception as e:
        logger.error(f"Unexpected error handling user join: {e}")
        db_session.rollback()
        return None

def get_session_users(session_id: str) -> List[Dict[str, Any]]:
    """获取会话用户列表"""
    if not validate_session_id(session_id):
        return []
    
    if not db_session:
        logger.error("Database session not initialized")
        return []
    
    try:
        # 获取会话中所有唯一的用户
        users = db_session.query(ChatMessage.user_id)\
            .filter_by(session_id=session_id)\
            .distinct()\
            .all()
        
        result = [{'user_id': user[0]} for user in users if user[0]]
        logger.info(f"Retrieved {len(result)} users for session {session_id}")
        return result
        
    except OperationalError as e:
        logger.error(f"Database operational error getting users: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error getting session users: {e}")
        return []

def get_session_info(session_id: str) -> Optional[Dict[str, Any]]:
    """获取会话信息"""
    if not validate_session_id(session_id):
        return None
    
    if not db_session:
        logger.error("Database session not initialized")
        return None
    
    try:
        session = db_session.query(ChatSession).filter_by(id=session_id).first()
        
        if session:
            result = {
                'id': session.id,
                'creator_id': session.creator_id,
                'ai_settings': session.ai_settings,
                'created_at': session.created_at.isoformat(),
                'updated_at': session.updated_at.isoformat()
            }
            logger.info(f"Retrieved session info: {session_id}")
            return result
        else:
            logger.warning(f"Session not found: {session_id}")
            return None
            
    except OperationalError as e:
        logger.error(f"Database operational error getting session info: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error getting session info: {e}")
        return None

def delete_session(session_id: str) -> bool:
    """删除会话"""
    if not validate_session_id(session_id):
        return False
    
    if not db_session:
        logger.error("Database session not initialized")
        return False
    
    try:
        session = db_session.query(ChatSession).filter_by(id=session_id).first()
        
        if session:
            # 删除相关消息
            deleted_messages = db_session.query(ChatMessage).filter_by(session_id=session_id).delete()
            logger.info(f"Deleted {deleted_messages} messages for session {session_id}")
            
            # 删除会话
            db_session.delete(session)
            db_session.commit()
            
            logger.info(f"Session deleted successfully: {session_id}")
            return True
        else:
            logger.warning(f"Session not found for deletion: {session_id}")
            return False
            
    except IntegrityError as e:
        logger.error(f"Integrity error deleting session: {e}")
        db_session.rollback()
        return False
    except OperationalError as e:
        logger.error(f"Database operational error deleting session: {e}")
        db_session.rollback()
        return False
    except Exception as e:
        logger.error(f"Unexpected error deleting session: {e}")
        db_session.rollback()
        return False

def update_session_settings(session_id: str, ai_settings: Dict[str, Any]) -> bool:
    """更新会话设置"""
    if not validate_session_id(session_id):
        return False
    
    if not isinstance(ai_settings, dict):
        logger.error("Invalid ai_settings")
        return False
    
    if not db_session:
        logger.error("Database session not initialized")
        return False
    
    try:
        session = db_session.query(ChatSession).filter_by(id=session_id).first()
        
        if session:
            session.ai_settings = ai_settings
            session.updated_at = datetime.utcnow()
            db_session.commit()
            
            logger.info(f"Session settings updated successfully: {session_id}")
            return True
        else:
            logger.warning(f"Session not found for settings update: {session_id}")
            return False
            
    except IntegrityError as e:
        logger.error(f"Integrity error updating session settings: {e}")
        db_session.rollback()
        return False
    except OperationalError as e:
        logger.error(f"Database operational error updating settings: {e}")
        db_session.rollback()
        return False
    except Exception as e:
        logger.error(f"Unexpected error updating session settings: {e}")
        db_session.rollback()
        return False

def get_session_stats(session_id: str) -> Optional[Dict[str, Any]]:
    """获取会话统计信息"""
    if not validate_session_id(session_id):
        return None
    
    if not db_session:
        logger.error("Database session not initialized")
        return None
    
    try:
        # 获取消息总数
        total_messages = db_session.query(ChatMessage)\
            .filter_by(session_id=session_id)\
            .count()
        
        # 获取用户消息数
        user_messages = db_session.query(ChatMessage)\
            .filter_by(session_id=session_id, sender_type='user')\
            .count()
        
        # 获取AI消息数
        ai_messages = db_session.query(ChatMessage)\
            .filter_by(session_id=session_id, sender_type='ai')\
            .count()
        
        # 获取唯一用户数
        unique_users = db_session.query(ChatMessage.user_id)\
            .filter_by(session_id=session_id)\
            .distinct()\
            .count()
        
        result = {
            'session_id': session_id,
            'total_messages': total_messages,
            'user_messages': user_messages,
            'ai_messages': ai_messages,
            'unique_users': unique_users,
            'last_updated': datetime.utcnow().isoformat()
        }
        
        logger.info(f"Retrieved session stats: {session_id}")
        return result
        
    except OperationalError as e:
        logger.error(f"Database operational error getting session stats: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error getting session stats: {e}")
        return None