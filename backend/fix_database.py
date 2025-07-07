#!/usr/bin/env python3
"""
数据库修复脚本
用于修复数据库表结构和数据
"""

import os
import sys
import traceback
from datetime import datetime
import uuid

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, ChatSession, ChatMessage

def fix_database():
    """修复数据库表结构和数据"""
    print("🔧 开始修复数据库...")
    print("=" * 50)
    
    with app.app_context():
        try:
            # 1. 创建所有表
            print("📋 创建数据库表...")
            db.create_all()
            print("✅ 数据库表创建完成")
            
            # 2. 检查并修复chat_sessions表
            print("\n🔍 检查chat_sessions表...")
            try:
                # 检查表是否存在
                result = db.session.execute("SELECT COUNT(*) FROM chat_sessions").scalar()
                print(f"✅ chat_sessions表存在，当前记录数: {result}")
            except Exception as e:
                print(f"❌ chat_sessions表不存在或有问题: {e}")
                print("🔄 重新创建chat_sessions表...")
                db.create_all()
            
            # 2.1 检查并修复chat_sessions表的title字段
            print("\n🔍 检查chat_sessions表的title字段...")
            try:
                # 检查title字段是否存在
                result = db.session.execute("SELECT column_name FROM information_schema.columns WHERE table_name='chat_sessions' AND column_name='title'").fetchone()
                if not result:
                    print("⚠️  chat_sessions表缺少title字段，正在添加...")
                    db.session.execute("ALTER TABLE chat_sessions ADD COLUMN title TEXT DEFAULT '';")
                    db.session.commit()
                    print("✅ 已添加title字段")
                else:
                    print("✅ chat_sessions表已包含title字段")
            except Exception as e:
                print(f"❌ 检查/添加title字段失败: {e}")
            
            # 3. 检查并修复chat_messages表
            print("\n🔍 检查chat_messages表...")
            try:
                # 检查表是否存在
                result = db.session.execute("SELECT COUNT(*) FROM chat_messages").scalar()
                print(f"✅ chat_messages表存在，当前记录数: {result}")
    except Exception as e:
                print(f"❌ chat_messages表不存在或有问题: {e}")
                print("🔄 重新创建chat_messages表...")
                db.create_all()
            
            # 4. 检查users表
            print("\n🔍 检查users表...")
            try:
                result = db.session.execute("SELECT COUNT(*) FROM users").scalar()
                print(f"✅ users表存在，当前用户数: {result}")
            except Exception as e:
                print(f"❌ users表不存在或有问题: {e}")
                print("🔄 重新创建users表...")
                db.create_all()
            
            # 5. 修复可能的数据问题
            print("\n🔧 修复数据问题...")
            
            # 检查是否有孤立的聊天消息（没有对应的会话）
            orphaned_messages = db.session.execute("""
                SELECT COUNT(*) FROM chat_messages 
                WHERE session_id NOT IN (SELECT id FROM chat_sessions)
            """).scalar()
            
            if orphaned_messages > 0:
                print(f"⚠️  发现 {orphaned_messages} 条孤立的聊天消息")
                print("🔄 为孤立消息创建默认会话...")
                
                # 为孤立消息创建默认会话
                default_session = ChatSession(
                    id=str(uuid.uuid4()),
                    user_id=1,  # 假设用户ID为1
                    ai_settings='{}',
                    created_at=datetime.utcnow()
                )
                db.session.add(default_session)
                
                # 更新孤立消息的session_id
                db.session.execute("""
                    UPDATE chat_messages 
                    SET session_id = :session_id 
                    WHERE session_id NOT IN (SELECT id FROM chat_sessions)
                """, {'session_id': default_session.id})
                
                db.session.commit()
                print("✅ 孤立消息修复完成")
            else:
                print("✅ 没有发现孤立消息")
            
            # 6. 检查外键约束
            print("\n🔍 检查外键约束...")
            try:
                # 检查用户外键
                invalid_user_messages = db.session.execute("""
                    SELECT COUNT(*) FROM chat_messages 
                    WHERE user_id NOT IN (SELECT id FROM users)
                """).scalar()
                
                if invalid_user_messages > 0:
                    print(f"⚠️  发现 {invalid_user_messages} 条消息的用户ID无效")
                else:
                    print("✅ 用户外键约束正常")
                
                # 检查会话外键
                invalid_session_messages = db.session.execute("""
                    SELECT COUNT(*) FROM chat_messages 
                    WHERE session_id NOT IN (SELECT id FROM chat_sessions)
                """).scalar()
                
                if invalid_session_messages > 0:
                    print(f"⚠️  发现 {invalid_session_messages} 条消息的会话ID无效")
                else:
                    print("✅ 会话外键约束正常")
                    
            except Exception as e:
                print(f"❌ 外键检查失败: {e}")
            
            print("\n" + "=" * 50)
            print("✅ 数据库修复完成！")
            
            # 7. 显示统计信息
            print("\n📊 数据库统计信息:")
            try:
                user_count = db.session.execute("SELECT COUNT(*) FROM users").scalar()
                session_count = db.session.execute("SELECT COUNT(*) FROM chat_sessions").scalar()
                message_count = db.session.execute("SELECT COUNT(*) FROM chat_messages").scalar()
                
                print(f"  用户数量: {user_count}")
                print(f"  会话数量: {session_count}")
                print(f"  消息数量: {message_count}")
                
            except Exception as e:
                print(f"❌ 统计信息获取失败: {e}")
        
    except Exception as e:
            print(f"❌ 数据库修复失败: {e}")
            traceback.print_exc()
        return False
    
    return True

def create_test_data():
    """创建测试数据"""
    print("\n🧪 创建测试数据...")
    
    with app.app_context():
        try:
            # 检查是否已有测试用户
            test_user = User.query.filter_by(username='testuser').first()
            if test_user:
                print("✅ 测试用户已存在")
                return test_user.id
            
            # 创建测试用户
            from werkzeug.security import generate_password_hash
            test_user = User(
                username='testuser',
                email='test@example.com',
                password_hash=generate_password_hash('test123')
            )
            db.session.add(test_user)
            db.session.flush()  # 获取用户ID
            
            # 创建测试会话
            test_session = ChatSession(
                id=str(uuid.uuid4()),
                user_id=test_user.id,
                ai_settings='{}',
                created_at=datetime.utcnow()
            )
            db.session.add(test_session)
            
            # 创建测试消息
            test_messages = [
                ChatMessage(
                    user_id=test_user.id,
                    session_id=test_session.id,
                    message_type='user',
                    content='你好，这是一个测试消息',
                    ai_models_used='[]',
                    timestamp=datetime.utcnow()
                ),
                ChatMessage(
                    user_id=test_user.id,
                    session_id=test_session.id,
                    message_type='ai',
                    content='你好！我是AI助手，很高兴为您服务。',
                    ai_models_used='["unified"]',
                    timestamp=datetime.utcnow()
                )
            ]
            
            for msg in test_messages:
                db.session.add(msg)
            
            db.session.commit()
            print("✅ 测试数据创建完成")
            return test_user.id
        
    except Exception as e:
            print(f"❌ 测试数据创建失败: {e}")
            db.session.rollback()
            return None

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--test-data':
        create_test_data()
    else:
        fix_database() 