#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask 后端：QQ群年度报告分析器线上版
正确流程：
1. 用户上传 → 2. 临时保存（OSS或本地） → 3. 后台下载分析 → 4. 删除临时文件
5. 用户选词 → 6. AI锐评 → 7. 保存MySQL（只存关键数据） → 8. 前端动态渲染
"""

import os
import json
import uuid
from typing import List, Dict
from datetime import datetime

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

os.environ['SKIP_OSS'] = '1'

# 将根目录加入路径
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import sys
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import config
import analyzer as analyzer_mod
from image_generator import ImageGenerator

from backend.oss_service import OSSService
from backend.db_service import DatabaseService


app = Flask(__name__)

# CORS配置 - 从环境变量读取
allowed_origins = os.getenv('ALLOWED_ORIGINS', 'http://localhost:5173,http://localhost:5000').split(',')
CORS(app, resources={
    r"/*": {
        "origins": allowed_origins,
        "supports_credentials": True
    }
})

# 文件上传限制 - 从环境变量读取
max_size_mb = int(os.getenv('MAX_UPLOAD_SIZE_MB', '50'))
app.config['MAX_CONTENT_LENGTH'] = max_size_mb * 1024 * 1024
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-please-change')

# 初始化服务
try:
    if os.getenv('SKIP_OSS') != '1':
        oss_service = OSSService()
    else:
        oss_service = None
        print("⚠️  OSS 功能已禁用，使用本地临时存储")
    db_service = DatabaseService()
    db_service.init_database()
except Exception as e:
    print(f"⚠️  服务初始化警告: {e}")
    oss_service = None
    db_service = None


def generate_ai_comments(selected_word_objects: List[Dict]) -> Dict[str, str]:
    """
    使用OpenAI API为每个热词生成犀利的AI锐评
    返回: {word: comment} 的字典
    """
    try:
        from image_generator import AICommentGenerator
        ai_gen = AICommentGenerator()
        
        if ai_gen.client:
            print("🤖 正在生成AI锐评...")
            comments = ai_gen.generate_batch(selected_word_objects)
            print("✅ AI锐评生成完成")
            return comments
        else:
            print("⚠️ OpenAI未配置，使用默认锐评")
            return {w['word']: ai_gen._fallback_comment(w['word']) 
                   for w in selected_word_objects}
    except Exception as e:
        print(f"⚠️ AI锐评生成失败: {e}")
        from image_generator import AICommentGenerator
        ai_gen = AICommentGenerator()
        return {w['word']: ai_gen._fallback_comment(w['word']) 
               for w in selected_word_objects}


@app.route("/api/health", methods=["GET"])
def health():
    """健康检查 - 提供详细的服务状态信息"""
    health_status = {
        "ok": True,
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "services": {
            "oss": {
                "enabled": oss_service is not None,
                "status": "healthy" if oss_service is not None else "disabled"
            },
            "database": {
                "enabled": db_service is not None,
                "status": "unknown"
            }
        }
    }
    
    # 检查数据库连接
    if db_service:
        try:
            # 尝试执行简单查询
            conn = db_service._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            conn.close()
            health_status["services"]["database"]["status"] = "healthy"
        except Exception as e:
            health_status["ok"] = False
            health_status["services"]["database"]["status"] = "unhealthy"
            health_status["services"]["database"]["error"] = str(e)
    
    # 检查存储目录
    try:
        base_dir = os.path.join(PROJECT_ROOT, "runtime_outputs")
        temp_dir = os.path.join(base_dir, "temp")
        os.makedirs(temp_dir, exist_ok=True)
        health_status["services"]["storage"] = {
            "status": "healthy",
            "path": temp_dir
        }
    except Exception as e:
        health_status["ok"] = False
        health_status["services"]["storage"] = {
            "status": "unhealthy",
            "error": str(e)
        }
    
    status_code = 200 if health_status["ok"] else 503
    return jsonify(health_status), status_code


def allowed_file(filename):
    """检查文件类型是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'json'


@app.route("/api/upload", methods=["POST"])
def upload_and_analyze():
    """
    步骤1-4: 上传→临时保存→分析→删除临时文件
    返回: report_id, 分析结果（热词列表供选择）
    """
    if not db_service:
        return jsonify({"error": "数据库服务未初始化"}), 500
    
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "缺少文件"}), 400
    
    # 验证文件类型
    if not allowed_file(file.filename):
        return jsonify({"error": "只允许上传JSON文件"}), 400

    # 获取是否AI自动选词
    auto_select = request.form.get("auto_select", "false").lower() == "true"
    
    # 生成report_id
    report_id = str(uuid.uuid4())
    
    # 临时保存文件
    base_dir = os.path.join(PROJECT_ROOT, "runtime_outputs")
    temp_dir = os.path.join(base_dir, "temp")
    os.makedirs(temp_dir, exist_ok=True)
    temp_path = os.path.join(temp_dir, f"{report_id}.json")
    file.save(temp_path)

    try:
        # 如果启用OSS：上传→获取URL→下载回来分析
        if oss_service:
            original_filename = file.filename or "chat.json"
            oss_key = oss_service.upload_json(temp_path, original_filename)
            # 这里可以选择从OSS下载回来，或直接使用本地文件
            # 为简化流程，直接使用本地文件
            local_file = temp_path
        else:
            local_file = temp_path
        
        # 解析并分析JSON
        data = json.load(open(local_file, encoding="utf-8-sig"))
        analyzer = analyzer_mod.ChatAnalyzer(data)
        analyzer.analyze()
        report = analyzer.export_json()
        
        # 获取热词列表
        all_words = report.get('topWords', [])[:100]
        
        # 如果是AI自动选词
        if auto_select:
            selected_words = [w['word'] for w in all_words[:10]]
            result = finalize_report(
                report_id=report_id,
                analyzer=analyzer,
                selected_words=selected_words,
                auto_mode=True
            )
            # 删除临时文件
            cleanup_temp_files(temp_path, oss_service, oss_key if oss_service else None)
            return result
        
        # 手动选词模式：返回热词列表，暂存分析结果
        # 将analyzer结果保存到临时文件供后续使用
        result_temp_path = os.path.join(temp_dir, f"{report_id}_result.json")
        with open(result_temp_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        return jsonify({
            "report_id": report_id,
            "chat_name": report.get('chatName', '未知群聊'),
            "message_count": report.get('messageCount', 0),
            "available_words": all_words
        })
    except Exception as exc:
        import traceback
        traceback.print_exc()
        # 清理临时文件
        cleanup_temp_files(temp_path, oss_service, None)
        return jsonify({"error": f"分析失败: {exc}"}), 500


@app.route("/api/finalize", methods=["POST"])
def finalize_report_endpoint():
    """
    步骤5-7: 用户选词 → AI锐评 → 保存MySQL
    """
    if not db_service:
        return jsonify({"error": "数据库服务未初始化"}), 500
    
    data = request.json
    report_id = data.get('report_id')
    selected_words = data.get('selected_words', [])
    
    if not report_id or not selected_words:
        return jsonify({"error": "缺少必要参数"}), 400
    
    try:
        # 从临时文件加载分析结果
        base_dir = os.path.join(PROJECT_ROOT, "runtime_outputs")
        temp_dir = os.path.join(base_dir, "temp")
        result_temp_path = os.path.join(temp_dir, f"{report_id}_result.json")
        
        if not os.path.exists(result_temp_path):
            return jsonify({"error": "分析结果已过期，请重新上传"}), 404
        
        with open(result_temp_path, 'r', encoding='utf-8') as f:
            report = json.load(f)
        
        # 重建analyzer（用于AI锐评）
        original_json_path = os.path.join(temp_dir, f"{report_id}.json")
        if os.path.exists(original_json_path):
            json_data = json.load(open(original_json_path, encoding="utf-8-sig"))
            analyzer = analyzer_mod.ChatAnalyzer(json_data)
            analyzer.analyze()
        else:
            analyzer = None
        
        result = finalize_report(
            report_id=report_id,
            analyzer=analyzer,
            selected_words=selected_words,
            auto_mode=False,
            report_data=report
        )
        
        # 清理临时文件
        cleanup_temp_files(result_temp_path, None, None)
        if os.path.exists(original_json_path):
            cleanup_temp_files(original_json_path, None, None)
        
        return result
    except Exception as exc:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"生成失败: {exc}"}), 500


def finalize_report(report_id: str, analyzer, selected_words: List[str], 
                   auto_mode: bool = False, report_data: Dict = None):
    """
    共用的报告最终化逻辑
    步骤5-7: 选词 + AI锐评 + 保存MySQL（只存关键数据）
    """
    try:
        if report_data is None:
            report = analyzer.export_json()
        else:
            report = report_data
        
        # 转换selected_words为详细对象
        all_words = {w['word']: w for w in report.get('topWords', [])}
        selected_word_objects = []
        for word in selected_words:
            if word in all_words:
                selected_word_objects.append(all_words[word])
            else:
                selected_word_objects.append({"word": word, "freq": 0, "samples": []})
        
        # 生成AI锐评（传入字典列表）
        ai_comments = generate_ai_comments(selected_word_objects)
        
        # 提取关键统计数据（只保留前端展示需要的）
        statistics = {
            "chatName": report.get('chatName'),
            "messageCount": report.get('messageCount'),
            "rankings": report.get('rankings', {}),
            "timeDistribution": report.get('timeDistribution', {}),
            "hourDistribution": report.get('hourDistribution', {})
        }
        
        # 保存到MySQL（只保存关键数据）
        success = db_service.create_report(
            report_id=report_id,
            chat_name=statistics['chatName'],
            message_count=statistics['messageCount'],
            selected_words=selected_word_objects,
            statistics=statistics,
            ai_comments=ai_comments
        )
        
        if not success:
            return jsonify({"error": "保存数据库失败"}), 500
        
        return jsonify({
            "success": True,
            "report_id": report_id,
            "report_url": f"/report/{report_id}",
            "message": "报告已生成" if not auto_mode else "AI已自动完成选词并生成报告"
        })
    except Exception as exc:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"最终化失败: {exc}"}), 500


def cleanup_temp_files(file_path: str, oss_service, oss_key: str = None):
    """清理临时文件"""
    try:
        # 删除本地临时文件
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            print(f"🗑️ 已删除临时文件: {file_path}")
        
        # 删除OSS文件
        if oss_service and oss_key:
            try:
                oss_service.delete_file(oss_key)
                print(f"🗑️ 已删除OSS文件: {oss_key}")
            except:
                pass
    except Exception as e:
        print(f"⚠️ 清理临时文件失败: {e}")


@app.route("/api/reports", methods=["GET"])
def list_reports():
    """查询报告列表"""
    if not db_service:
        return jsonify({"error": "数据库服务未初始化"}), 500
    
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('page_size', 20))
    chat_name = request.args.get('chat_name')
    
    try:
        result = db_service.list_reports(page, page_size, chat_name)
        return jsonify(result)
    except Exception as exc:
        return jsonify({"error": f"查询失败: {exc}"}), 500


@app.route("/api/reports/<report_id>", methods=["GET"])
@app.route("/report/<report_id>", methods=["GET"])
def get_report(report_id):
    """
    获取报告数据（返回JSON供前端动态渲染）
    同时支持 /api/reports/{id} 和 /report/{id} 两个路径
    """
    if not db_service:
        return jsonify({"error": "数据库服务未初始化"}), 500
    
    try:
        report = db_service.get_report(report_id)
        if not report:
            return jsonify({"error": "报告不存在"}), 404
        
        # 使用ImageGenerator的数据处理逻辑
        processed_data = process_report_data_for_frontend(report)
        
        return jsonify(processed_data)
    except Exception as exc:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"获取失败: {exc}"}), 500


@app.route("/api/reports/<report_id>", methods=["DELETE"])
def delete_report(report_id):
    """删除报告"""
    if not db_service:
        return jsonify({"error": "数据库服务未初始化"}), 500
    
    try:
        success = db_service.delete_report(report_id)
        if not success:
            return jsonify({"error": "报告不存在"}), 404
        
        return jsonify({"success": True, "message": "报告已删除"})
    except Exception as exc:
        return jsonify({"error": f"删除失败: {exc}"}), 500


def process_report_data_for_frontend(report):
    """
    使用ImageGenerator的逻辑处理报告数据为前端需要的格式
    复用image_generator.py中的_prepare_template_data方法
    """
    # 构建一个临时的ImageGenerator实例来使用其数据处理方法
    # 模拟json_data结构
    json_data = {
        'chatName': report['chat_name'],
        'messageCount': report['message_count'],
        'topWords': report['selected_words'],  # 这里已经包含完整的词信息
        'rankings': report['statistics'].get('rankings', {}),
        'hourDistribution': report['statistics'].get('hourDistribution', {})
    }
    
    # 创建ImageGenerator实例
    gen = ImageGenerator()
    gen.json_data = json_data
    gen.selected_words = report['selected_words']  # 设置选中的词
    gen.ai_comments = report.get('ai_comments', {}) or {}  # 设置AI评语
    
    # 调用其数据处理方法
    template_data = gen._prepare_template_data()
    
    # 返回前端需要的格式，确保AI评语被正确包含
    return {
        "report_id": report['report_id'],
        "chat_name": template_data['chat_name'],
        "message_count": template_data['message_count'],
        "selected_words": template_data['selected_words'],  # 这里已经包含ai_comment
        "rankings": template_data['rankings'],  # 这里已经是处理好的榜单
        "statistics": {
            "hourDistribution": {str(h['hour']): h['count'] for h in template_data['hour_data']}
        },
        "peak_hour": template_data['peak_hour'],
        "created_at": str(report['created_at'])
    }


@app.route("/api/demo", methods=["GET"])
def get_demo_file():
    """
    提供演示数据文件供下载
    用户可以下载这个文件快速体验系统功能
    """
    demo_file_path = os.path.join(PROJECT_ROOT, "demo_chat.json")
    
    # 如果演示文件不存在，动态生成
    if not os.path.exists(demo_file_path):
        try:
            import subprocess
            result = subprocess.run(
                ["python", os.path.join(PROJECT_ROOT, "generate_demo_data.py")],
                cwd=PROJECT_ROOT,
                check=True,
                capture_output=True,
                text=True
            )
        except subprocess.CalledProcessError as e:
            return jsonify({
                "error": f"生成演示数据失败: {e.stderr or e.stdout or str(e)}"
            }), 500
        except Exception as e:
            return jsonify({"error": f"生成演示数据失败: {str(e)}"}), 500
    
    if os.path.exists(demo_file_path):
        return send_file(
            demo_file_path,
            mimetype='application/json',
            as_attachment=True,
            download_name='demo_chat.json'
        )
    else:
        return jsonify({"error": "演示文件不存在"}), 404


@app.errorhandler(404)
def not_found(error):
    """404 错误处理"""
    return jsonify({
        "error": "接口不存在",
        "message": "请检查 API 路径是否正确",
        "available_endpoints": [
            "GET /api/health - 健康检查",
            "POST /api/upload - 上传并分析",
            "POST /api/finalize - 完成报告",
            "GET /api/reports - 查询报告列表",
            "GET /api/reports/{id} - 获取报告详情",
            "DELETE /api/reports/{id} - 删除报告",
            "GET /api/demo - 下载演示数据"
        ]
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """500 错误处理"""
    return jsonify({
        "error": "服务器内部错误",
        "message": "请稍后重试或联系管理员"
    }), 500


@app.errorhandler(413)
def request_entity_too_large(error):
    """文件过大错误处理"""
    max_size = app.config.get('MAX_CONTENT_LENGTH', 50 * 1024 * 1024) // (1024 * 1024)
    return jsonify({
        "error": "文件过大",
        "message": f"文件大小不能超过 {max_size} MB"
    }), 413


if __name__ == "__main__":
    debug_mode = os.environ.get("DEBUG", "").lower() in ("1", "true", "yes")
    base_port = int(os.environ.get("FLASK_PORT", os.environ.get("PORT", 5000)))

    def try_run(p):
        app.run(host="0.0.0.0", port=p, debug=debug_mode, use_reloader=False)

    try:
        try_run(base_port)
    except OSError as exc:
        if "Address already in use" in str(exc):
            fallback = base_port + 1
            print(f"⚠️ 端口 {base_port} 已被占用，尝试 {fallback}")
            try_run(fallback)
        else:
            raise
