#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库迁移脚本
用于升级数据库结构而不丢失数据
"""

import os
import pymysql
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


def get_db_connection():
    """获取数据库连接"""
    return pymysql.connect(
        host=os.getenv('MYSQL_HOST', 'localhost'),
        port=int(os.getenv('MYSQL_PORT', 3306)),
        user=os.getenv('MYSQL_USER', 'root'),
        password=os.getenv('MYSQL_PASSWORD', ''),
        database=os.getenv('MYSQL_DATABASE', 'qq_reports'),
        charset=os.getenv('MYSQL_CHARSET', 'utf8mb4')
    )


def get_current_version(conn):
    """获取当前数据库版本"""
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT version FROM schema_version 
            ORDER BY applied_at DESC LIMIT 1
        """)
        result = cursor.fetchone()
        cursor.close()
        return result[0] if result else 0
    except pymysql.err.ProgrammingError:
        # 表不存在，创建版本表
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS schema_version (
                id INT AUTO_INCREMENT PRIMARY KEY,
                version INT NOT NULL,
                description VARCHAR(255),
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        cursor.close()
        return 0


def apply_migration(conn, version, description, sql):
    """应用一个迁移"""
    cursor = conn.cursor()
    try:
        # 执行迁移 SQL
        for statement in sql.split(';'):
            if statement.strip():
                cursor.execute(statement)
        
        # 记录版本
        cursor.execute("""
            INSERT INTO schema_version (version, description)
            VALUES (%s, %s)
        """, (version, description))
        
        conn.commit()
        print(f"✅ 已应用迁移 v{version}: {description}")
        return True
    except Exception as e:
        conn.rollback()
        print(f"❌ 迁移 v{version} 失败: {e}")
        return False
    finally:
        cursor.close()


def migrate():
    """执行数据库迁移"""
    print("🔄 开始数据库迁移...")
    
    conn = get_db_connection()
    current_version = get_current_version(conn)
    print(f"📊 当前数据库版本: v{current_version}")
    
    # 定义迁移
    migrations = [
        # 示例迁移 - 添加索引以提高查询性能
        {
            "version": 1,
            "description": "添加索引优化查询性能",
            "sql": """
                CREATE INDEX idx_created_at ON reports(created_at);
                CREATE INDEX idx_chat_name ON reports(chat_name);
            """
        },
        # 示例迁移 - 添加报告分享功能字段
        {
            "version": 2,
            "description": "添加报告分享功能",
            "sql": """
                ALTER TABLE reports ADD COLUMN share_token VARCHAR(64) UNIQUE AFTER report_id;
                ALTER TABLE reports ADD COLUMN is_public BOOLEAN DEFAULT FALSE AFTER share_token;
            """
        },
        # 可以继续添加更多迁移...
    ]
    
    # 应用需要的迁移
    applied_count = 0
    for migration in migrations:
        if migration['version'] > current_version:
            success = apply_migration(
                conn,
                migration['version'],
                migration['description'],
                migration['sql']
            )
            if success:
                applied_count += 1
            else:
                print("⚠️  迁移失败，停止后续迁移")
                break
    
    conn.close()
    
    if applied_count > 0:
        print(f"\n✅ 成功应用 {applied_count} 个迁移")
    else:
        print("\n✅ 数据库已是最新版本，无需迁移")
    
    return applied_count


if __name__ == "__main__":
    try:
        migrate()
    except Exception as e:
        print(f"❌ 迁移失败: {e}")
        exit(1)
