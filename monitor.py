#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统监控脚本
监控服务状态、资源使用、日志等
"""

import os
import sys
import json
import time
import requests
from datetime import datetime


def check_service_health(base_url):
    """检查服务健康状态"""
    try:
        response = requests.get(f"{base_url}/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return True, data
        else:
            return False, {"error": f"HTTP {response.status_code}"}
    except requests.exceptions.RequestException as e:
        return False, {"error": str(e)}


def check_disk_space(path="/"):
    """检查磁盘空间"""
    try:
        import shutil
        total, used, free = shutil.disk_usage(path)
        return {
            "total_gb": round(total / (1024**3), 2),
            "used_gb": round(used / (1024**3), 2),
            "free_gb": round(free / (1024**3), 2),
            "used_percent": round((used / total) * 100, 2)
        }
    except Exception as e:
        return {"error": str(e)}


def check_database_status():
    """检查数据库状态"""
    try:
        from dotenv import load_dotenv
        import pymysql
        
        load_dotenv()
        
        conn = pymysql.connect(
            host=os.getenv('MYSQL_HOST', 'localhost'),
            port=int(os.getenv('MYSQL_PORT', 3306)),
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', ''),
            database=os.getenv('MYSQL_DATABASE', 'qq_reports'),
            connect_timeout=5
        )
        
        cursor = conn.cursor()
        
        # 获取报告数量
        cursor.execute("SELECT COUNT(*) FROM reports")
        report_count = cursor.fetchone()[0]
        
        # 获取数据库大小
        cursor.execute("""
            SELECT 
                ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) as size_mb
            FROM information_schema.tables
            WHERE table_schema = %s
        """, (os.getenv('MYSQL_DATABASE', 'qq_reports'),))
        size_result = cursor.fetchone()
        db_size = size_result[0] if size_result[0] else 0
        
        cursor.close()
        conn.close()
        
        return {
            "status": "healthy",
            "report_count": report_count,
            "database_size_mb": db_size
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


def monitor():
    """执行监控检查"""
    print("=" * 60)
    print(f"系统监控报告 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 检查 Web 服务
    print("\n📡 Web 服务状态:")
    backend_url = os.getenv('BACKEND_URL', 'http://localhost:5000')
    healthy, health_data = check_service_health(backend_url)
    
    if healthy:
        print("  ✅ 后端服务: 正常")
        print(f"  版本: {health_data.get('version', 'unknown')}")
        for service, info in health_data.get('services', {}).items():
            status = info.get('status', 'unknown') if isinstance(info, dict) else ('enabled' if info else 'disabled')
            print(f"  - {service}: {status}")
    else:
        print(f"  ❌ 后端服务: 异常")
        print(f"  错误: {health_data.get('error', 'unknown')}")
    
    # 检查数据库
    print("\n💾 数据库状态:")
    db_status = check_database_status()
    if db_status.get('status') == 'healthy':
        print("  ✅ 数据库: 正常")
        print(f"  报告数量: {db_status.get('report_count', 0)}")
        print(f"  数据库大小: {db_status.get('database_size_mb', 0)} MB")
    else:
        print(f"  ❌ 数据库: 异常")
        print(f"  错误: {db_status.get('error', 'unknown')}")
    
    # 检查磁盘空间
    print("\n💿 磁盘空间:")
    disk_info = check_disk_space()
    if 'error' not in disk_info:
        print(f"  总容量: {disk_info['total_gb']} GB")
        print(f"  已使用: {disk_info['used_gb']} GB ({disk_info['used_percent']}%)")
        print(f"  可用空间: {disk_info['free_gb']} GB")
        
        if disk_info['used_percent'] > 90:
            print("  ⚠️  警告: 磁盘空间不足!")
        elif disk_info['used_percent'] > 80:
            print("  ⚠️  提示: 磁盘空间较少")
        else:
            print("  ✅ 磁盘空间充足")
    else:
        print(f"  ❌ 无法获取磁盘信息: {disk_info.get('error')}")
    
    # 检查运行时目录
    print("\n📁 运行时目录:")
    runtime_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'runtime_outputs')
    if os.path.exists(runtime_dir):
        try:
            file_count = sum([len(files) for r, d, files in os.walk(runtime_dir)])
            print(f"  路径: {runtime_dir}")
            print(f"  文件数: {file_count}")
            print("  ✅ 目录正常")
        except Exception as e:
            print(f"  ❌ 无法访问目录: {e}")
    else:
        print(f"  ⚠️  目录不存在: {runtime_dir}")
    
    print("\n" + "=" * 60)
    
    # 返回整体健康状态
    return healthy and db_status.get('status') == 'healthy'


if __name__ == "__main__":
    try:
        # 支持持续监控模式
        if len(sys.argv) > 1 and sys.argv[1] == "--watch":
            interval = int(sys.argv[2]) if len(sys.argv) > 2 else 60
            print(f"🔄 持续监控模式 (每 {interval} 秒刷新)")
            while True:
                is_healthy = monitor()
                if not is_healthy:
                    print("⚠️  系统存在问题，请检查!")
                time.sleep(interval)
        else:
            # 单次检查
            is_healthy = monitor()
            exit(0 if is_healthy else 1)
    except KeyboardInterrupt:
        print("\n\n👋 监控已停止")
        exit(0)
    except Exception as e:
        print(f"\n❌ 监控失败: {e}")
        exit(1)
