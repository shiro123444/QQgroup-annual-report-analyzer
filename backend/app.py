#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask 后端：提供上传、分析、报告生成接口。
"""

import os
import json
import tempfile
import importlib
from typing import Any, Dict

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS

# 将根目录加入路径，便于复用现有模块
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import sys

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import config  # noqa: E402
import analyzer as analyzer_mod  # noqa: E402
import report_generator as report_mod  # noqa: E402
import image_generator as image_mod  # noqa: E402


def apply_overrides(overrides: Dict[str, Any]) -> None:
    """将前端传入的参数覆写到 config 模块，并刷新下游依赖。"""
    importlib.reload(config)
    for key, val in overrides.items():
        if hasattr(config, key):
            setattr(config, key, val)
    importlib.reload(analyzer_mod)
    importlib.reload(report_mod)
    importlib.reload(image_mod)


def reset_config() -> None:
    """恢复 config 为默认值（从 config.py 重新加载）。"""
    importlib.reload(config)
    importlib.reload(analyzer_mod)
    importlib.reload(report_mod)
    importlib.reload(image_mod)


app = Flask(__name__)
# 开放 CORS（如需可按域名限制）
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"ok": True})


@app.route("/api/analyze", methods=["POST"])
def analyze():
    file = request.files.get("file")
    if not file:
        return jsonify({"error": "缺少文件"}), 400

    # 解析可选参数
    try:
        options = json.loads(request.form.get("options", "{}"))
    except Exception:
        options = {}

    # 默认行为：尊重 config，允许前端覆盖
    options.setdefault("ENABLE_IMAGE_EXPORT", config.ENABLE_IMAGE_EXPORT)
    options.setdefault("GENERATE_PNG", False)

    base_dir = os.path.join(PROJECT_ROOT, "runtime_outputs")
    os.makedirs(base_dir, exist_ok=True)
    tmpdir = tempfile.mkdtemp(dir=base_dir)
    input_path = os.path.join(tmpdir, "chat.json")
    file.save(input_path)

    try:
        data = json.load(open(input_path, encoding="utf-8-sig"))
    except Exception as exc:
        return jsonify({"error": f"JSON 解析失败: {exc}"}), 400

    # 应用参数
    apply_overrides(options)

    try:
        analyzer = analyzer_mod.ChatAnalyzer(data)
        analyzer.analyze()
        report = analyzer.export_json()

        # 生成文本报告
        reporter = report_mod.ReportGenerator(analyzer, output_dir=tmpdir)
        txt_path = reporter.generate_file_report()

        html_path = None
        png_path = None

        # 按需生成 HTML/图片
        if options.get("ENABLE_IMAGE_EXPORT"):
            img_gen = image_mod.ImageGenerator(analyzer=analyzer, output_dir=tmpdir)
            html_path, png_path = img_gen.generate(
                auto_select=True,
                non_interactive=True,
                generate_image=options.get("GENERATE_PNG", False),
            )

        resp = {
            "result": report,
            "txt_report": txt_path,
            "html_report": html_path,
            "png_report": png_path,
        }
        return jsonify(resp)
    except Exception as exc:
        return jsonify({"error": f"分析失败: {exc}"}), 500
    finally:
        reset_config()


@app.route("/api/download", methods=["GET"])
def download():
    path = request.args.get("path")
    if not path or not os.path.exists(path):
        return jsonify({"error": "文件不存在"}), 404
    return send_file(path, as_attachment=True)


if __name__ == "__main__":
    # DEBUG=1 可开启调试模式；默认关闭以避免重启进程导致的异常捕获失效
    debug_mode = os.environ.get("DEBUG", "").lower() in ("1", "true", "yes")
    base_port = int(os.environ.get("PORT", 5000))

    def try_run(p):
        app.run(host="0.0.0.0", port=p, debug=debug_mode, use_reloader=False)

    try:
        try_run(base_port)
    except OSError as exc:
        if "Address already in use" in str(exc):
            fallback = base_port + 1
            print(f"⚠️ 端口 {base_port} 已被占用，自动尝试 {fallback}。如需自定义端口：PORT=xxxx python app.py")
            try_run(fallback)
        else:
            raise

