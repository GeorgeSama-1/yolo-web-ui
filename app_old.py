#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask + YOLOv8 绝缘子检测 Web 应用
支持 Canvas 交互式可视化和实时参数调整

Updated to serve Vue 3 + Vite built static files
"""

from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from pathlib import Path
import cv2
import numpy as np
import json
from ultralytics import YOLO
import io
from datetime import datetime
import sys
import os

# 添加父目录到 Python 路径，以便导入 config
sys.path.append(str(Path(__file__).parent.parent))

# ==================== 路径配置 ====================
# Flask app 的目录（web_ui 就是当前目录）
WEB_UI_DIR = Path(__file__).parent.resolve()
# Vue 构建输出的 dist 目录（在 web_ui 文件夹内）
VUE_DIST_DIR = WEB_UI_DIR / 'web_ui_vite' / 'dist'

# 导入配置
try:
    from config import (
        BASE_DIR, MODEL_PATH, CONFIDENCE_THRESHOLD,
        UPLOAD_FOLDER, OUTPUT_FOLDER, HOST, PORT, DEBUG,
        MAX_CONTENT_LENGTH, MAX_HISTORY
    )
except ImportError:
    # 如果配置文件不存在，使用默认配置
    BASE_DIR = Path(__file__).parent.parent
    MODEL_PATH = BASE_DIR / 'experiments/20260210_092222_bbox_yolo11x_exp003_bs8_is1280_gpu2_datav2/weights/best.pt'
    CONFIDENCE_THRESHOLD = 0.8
    UPLOAD_FOLDER = WEB_UI_DIR / 'uploads'
    OUTPUT_FOLDER = WEB_UI_DIR / 'outputs'
    HOST = '0.0.0.0'
    PORT = 5000
    DEBUG = True
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024
    MAX_HISTORY = 20

app = Flask(__name__, static_folder=str(VUE_DIST_DIR / 'assets'), template_folder=str(VUE_DIST_DIR))
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# ==================== CORS 配置 ====================
# 允许 Vite 开发服务器（localhost:5173）在开发模式下访问 API
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5173", "http://127.0.0.1:5173"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    },
    r"/download/*": {
        "origins": ["http://localhost:5173", "http://127.0.0.1:5173"],
        "methods": ["GET", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# 创建必要的目录
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

# 加载模型
os.environ['CUDA_VISIBLE_DEVICES'] = '6'  # 指定GPU 6进行推理

# ==================== 模型配置 ====================
def parse_experiment_name(exp_name):
    """
    解析实验目录名称，提取信息

    格式: YYYYMMDD_HHMMSS_<task>_<model>_exp<NUM>_bs<BS>_is<IS>_<gpu-info>_<data-version>
    示例: 20260210_092222_bbox_yolo11x_exp003_bs8_is1280_gpu2_datav2
    """
    parts = exp_name.split('_')

    info = {
        'timestamp': f"{parts[0]}_{parts[1]}",  # 日期时间
        'task': parts[2] if len(parts) > 2 else 'unknown',  # 任务类型 (bbox)
        'model': parts[3] if len(parts) > 3 else 'unknown',  # 模型名称 (yolo11x)
    }

    # 解析其他参数
    for part in parts:
        if part.startswith('exp'):
            info['exp'] = part
        elif part.startswith('bs'):
            info['batch_size'] = part[2:]  # bs8 -> 8
        elif part.startswith('is'):
            info['img_size'] = part[2:]  # is1280 -> 1280
        elif part.startswith('gpu'):
            info['gpu'] = part
        elif part.startswith('data'):
            info['data_version'] = part  # datav2, datav3

    return info


def discover_models():
    """
    自动扫描 experiments 目录，发现所有可用模型
    """
    models = {}
    experiments_dir = BASE_DIR / 'experiments'

    if not experiments_dir.exists():
        return models

    # 查找所有 best.pt 文件
    for model_path in experiments_dir.glob('*/weights/best.pt'):
        exp_dir = model_path.parent.parent
        exp_name = exp_dir.name

        # 解析实验名称
        info = parse_experiment_name(exp_name)

        # 生成友好的模型名称
        model_type = info.get('model', 'unknown').upper()
        data_version = info.get('data_version', 'unknown')
        img_size = info.get('img_size', '?')
        batch_size = info.get('batch_size', '?')
        exp_num = info.get('exp', '?')

        # 生成唯一key和描述
        key = exp_name
        name = f"{model_type} ({data_version})"

        # 构建详细描述
        desc_parts = []
        desc_parts.append(f"Exp{exp_num.split('exp')[1] if 'exp' in exp_num else '?'}")
        desc_parts.append(f"BS{batch_size}")
        desc_parts.append(f"IS{img_size}")
        if 'gpu' in info:
            desc_parts.append(info['gpu'])
        desc_parts.append(data_version)

        description = ' '.join(desc_parts)

        models[key] = {
            'name': name,
            'path': model_path,
            'description': description,
            'exp_name': exp_name,
            'exists': True
        }

    # 按时间戳排序（最新的在前）
    sorted_models = dict(sorted(
        models.items(),
        key=lambda x: x[1]['exp_name'],
        reverse=True
    ))

    return sorted_models


# 自动发现所有模型
AVAILABLE_MODELS = discover_models()

# 当前使用的模型
# 使用最新的模型（第一个）作为默认模型
current_model_key = list(AVAILABLE_MODELS.keys())[0] if AVAILABLE_MODELS else None
model = None

def load_model(model_key):
    """加载指定的模型"""
    global model, current_model_key

    if model_key not in AVAILABLE_MODELS:
        raise ValueError(f"未知的模型: {model_key}")

    model_info = AVAILABLE_MODELS[model_key]
    model_path = model_info['path']

    if not model_path.exists():
        raise FileNotFoundError(f"模型文件不存在: {model_path}")

    print(f"正在加载模型: {model_info['name']}...")
    model = YOLO(str(model_path))
    current_model_key = model_key

    print(f"✓ 模型加载完成: {model_info['name']}")
    print(f"  路径: {model_path}")
    print(f"  描述: {model_info['description']}")

    return model_info

print("=" * 60)
print("绝缘子检测 Web UI (Vue 3 + Vite 版本)")
print("使用 GPU 6 进行推理")
print("=" * 60)

# 初始化加载默认模型
load_model(current_model_key)

print(f"✓ 置信度阈值: {CONFIDENCE_THRESHOLD}")
print(f"✓ 上传目录: {UPLOAD_FOLDER.absolute()}")
print(f"✓ 导出目录: {OUTPUT_FOLDER.absolute()}")
print(f"✓ Vue 构建目录: {VUE_DIST_DIR.absolute()}")
print("=" * 60)


# ==================== 静态文件服务 ====================

@app.route('/')
def index():
    """
    主页 - 服务 Vue 构建的 index.html
    """
    if VUE_DIST_DIR.exists():
        return send_from_directory(VUE_DIST_DIR, 'index.html')
    else:
        return """
        <html>
        <head><title>Vue App Not Built</title></head>
        <body>
        <h1>Vue 应用未构建</h1>
        <p>请先运行以下命令构建 Vue 应用：</p>
        <pre>
        cd web_ui_vite
        npm run build
        </pre>
        <p>或者使用开发模式：</p>
        <pre>
        cd web_ui_vite
        npm run dev
        </pre>
        </body>
        </html>
        """, 503


@app.route('/assets/<path:filename>')
def serve_assets(filename):
    """
    服务 Vue 构建的静态资源 (JS, CSS)
    """
    return send_from_directory(VUE_DIST_DIR / 'assets', filename)


@app.route('/<path:path>')
def serve_spa(path):
    """
    SPA 路由支持 - 所有非 API 和非 download 请求都返回 index.html
    这样 Vue Router 可以处理前端路由
    """
    # 跳过 API 和 download 请求
    if path.startswith('api/') or path.startswith('download/'):
        from flask import abort
        abort(404)

    # 检查是否是静态资源请求
    if '.' in path.split('/')[-1]:
        # 可能是静态文件，尝试从 dist 目录提供
        file_path = VUE_DIST_DIR / path
        if file_path.exists() and file_path.is_file():
            return send_from_directory(VUE_DIST_DIR, path)

    # 返回 index.html 支持 Vue Router
    return send_from_directory(VUE_DIST_DIR, 'index.html')


# ==================== API 路由（保持原有逻辑不变）====================

@app.route('/api/models', methods=['GET'])
def get_models():
    """获取所有可用模型列表"""
    # 重新扫描模型（确保显示最新状态）
    global AVAILABLE_MODELS
    AVAILABLE_MODELS = discover_models()

    models_list = []
    for key, info in AVAILABLE_MODELS.items():
        # 检查文件是否实际存在
        exists = info['path'].exists()

        models_list.append({
            'key': key,
            'name': info['name'],
            'description': info['description'],
            'exists': exists,
            'exp_name': info.get('exp_name', key)
        })
    return jsonify({
        'models': models_list,
        'current_model': current_model_key
    })


@app.route('/api/switch_model', methods=['POST'])
def switch_model():
    """切换模型"""
    data = request.json
    model_key = data.get('model_key')

    if not model_key:
        return jsonify({'error': '未指定模型'}), 400

    if model_key not in AVAILABLE_MODELS:
        return jsonify({'error': f'未知的模型: {model_key}'}), 400

    try:
        model_info = load_model(model_key)
        return jsonify({
            'success': True,
            'model_key': model_key,
            'model_name': model_info['name'],
            'description': model_info['description']
        })
    except FileNotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': f'模型加载失败: {str(e)}'}), 500


@app.route('/api/upload', methods=['POST'])
def upload_image():
    """
    处理图片上传和 YOLO 推理
    返回检测结果（不画框，只返回坐标）
    """
    if 'image' not in request.files:
        return jsonify({'error': '没有上传图片'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400

    try:
        # 保存上传的图片
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 优先使用前端传递的 original_path，否则使用 file.filename
        # original_path 包含完整的相对路径，如 "173/二线绝缘子/image.jpg"
        original_path = request.form.get('original_path', file.filename)

        # 调试：打印收到的原始路径
        print(f"📁 上传文件: original_path='{original_path}', file.filename='{file.filename}'")

        # 生成保存的文件名（带时间戳前缀，替换路径分隔符避免目录问题）
        # 将原始路径中的 / 替换为 _ 以确保文件名有效
        safe_filename = original_path.replace('/', '_').replace('\\', '_')
        filename = f"{timestamp}_{safe_filename}"
        image_path = UPLOAD_FOLDER / filename
        file.save(str(image_path))

        # 读取原图用于返回
        original_img = cv2.imread(str(image_path))

        # YOLO 推理
        results = model.predict(str(image_path), conf=0.25)
        result = results[0]

        # 提取检测框信息并绘制（参考 notebook 的高对比度配色）
        detections = []

        # 创建绘制图片的副本
        annotated_img = original_img.copy()

        for box in result.boxes:
            xyxy = box.xyxy[0].cpu().numpy()
            x1, y1, x2, y2 = map(int, xyxy)
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])

            # 过滤低置信度检测框
            if conf < CONFIDENCE_THRESHOLD:
                continue

            detections.append({
                'id': len(detections) + 1,  # 重新编号
                'class_id': cls_id,
                'class_name': 'insulator',
                'confidence': conf,
                'bbox': xyxy.tolist()  # [x1, y1, x2, y2]
            })

            # 参考 notebook 的绘制方式：红色边框 + 黄色半透明填充
            # 边框颜色：红色 (BGR格式: 0, 0, 255)
            box_color = (0, 0, 255)

            # 填充颜色：黄色半透明 (BGR格式: 0, 255, 255)
            fill_color = (0, 255, 255)

            # 绘制半透明填充
            overlay = annotated_img.copy()
            cv2.rectangle(overlay, (x1, y1), (x2, y2), fill_color, -1)
            cv2.addWeighted(annotated_img, 0.7, overlay, 0.3, 0, annotated_img)

            # 绘制边框（适中线宽=2）
            cv2.rectangle(annotated_img, (x1, y1), (x2, y2), box_color, 2)

            # 添加标签和置信度
            label = f"Insulator {conf:.2f}"

            # 标签背景
            (text_w, text_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            cv2.rectangle(annotated_img, (x1, y1 - text_h - 8), (x1 + text_w + 4, y1), (0, 0, 0), -1)

            # 标签文字（白色）
            cv2.putText(annotated_img, label, (x1 + 2, y1 - 4),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        # 将绘制好的图片转换为 base64 用于前端显示
        import base64
        _, buffer = cv2.imencode('.jpg', annotated_img)
        img_base64 = base64.b64encode(buffer).decode('utf-8')

        # 生成缩略图（用于历史记录，减少内存占用）
        thumb_height = 150
        thumb_width = int(annotated_img.shape[1] * (thumb_height / annotated_img.shape[0]))
        thumbnail = cv2.resize(annotated_img, (thumb_width, thumb_height))
        _, thumb_buffer = cv2.imencode('.jpg', thumbnail, [cv2.IMWRITE_JPEG_QUALITY, 70])
        thumb_base64 = base64.b64encode(thumb_buffer).decode('utf-8')

        # 获取当前使用的模型信息
        model_info = AVAILABLE_MODELS.get(current_model_key, {})

        return jsonify({
            'success': True,
            'image_id': timestamp,
            'image_path': filename,
            'image_name': file.filename,  # 原始文件名（包含相对路径）
            'original_path': original_path,  # 原始相对路径（用于文件夹分组）
            'image_base64': img_base64,
            'thumbnail_base64': thumb_base64,  # 添加缩略图
            'image_width': annotated_img.shape[1],
            'image_height': annotated_img.shape[0],
            'detections': detections,
            'insulator_count': len(detections),
            'total_count': len(detections),
            # 添加模型信息
            'model_info': {
                'key': current_model_key,
                'name': model_info.get('name', 'Unknown'),
                'description': model_info.get('description', '')
            }
        })

    except Exception as e:
        return jsonify({'error': f'处理失败: {str(e)}'}), 500


@app.route('/api/export_labelme', methods=['POST'])
def export_labelme():
    """
    导出 LabelMe 格式的 JSON 标注文件
    """
    data = request.json
    image_path = UPLOAD_FOLDER / data['image_path']

    if not image_path.exists():
        return jsonify({'error': '图像不存在'}), 404

    try:
        # 读取图像获取尺寸
        img = cv2.imread(str(image_path))
        img_height, img_width = img.shape[:2]

        # 构建 LabelMe 格式
        labelme_data = {
            'version': '5.10.1',
            'flags': {},
            'shapes': [],
            'imagePath': image_path.name,
            'imageHeight': img_height,
            'imageWidth': img_width
        }

        # 添加检测框
        for det in data['detections']:
            x1, y1, x2, y2 = det['bbox']

            labelme_data['shapes'].append({
                'label': det['class_name'],
                'points': [
                    [x1, y1],
                    [x2, y2]
                ],
                'group_id': None,
                'shape_type': 'rectangle',
                'flags': {},
                'mask': None
            })

        # 获取模型信息（如果有）
        model_info = data.get('model_info', {})
        model_suffix = ''
        if model_info.get('name'):
            # 从模型名称中提取简短标识，如 "YOLO11X (datav4)" -> "_yolo11x_datav4"
            model_name = model_info.get('name', '').lower()
            # 简化模型名：移除空格和括号
            model_suffix = '_' + model_name.replace(' ', '_').replace('(', '').replace(')', '')

        # 保存 JSON 文件（文件名包含模型标识）
        json_path = OUTPUT_FOLDER / f"{image_path.stem}{model_suffix}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(labelme_data, f, indent=2, ensure_ascii=False)

        return jsonify({
            'success': True,
            'json_path': json_path.name,
            'download_url': f'/download/{json_path.name}'
        })

    except Exception as e:
        return jsonify({'error': f'导出失败: {str(e)}'}), 500


@app.route('/api/batch_export_labelme', methods=['POST'])
def batch_export_labelme():
    """
    批量导出 LabelMe 格式的 JSON 标注文件为 ZIP 包
    """
    import zipfile

    data = request.json
    items = data.get('items', [])

    if not items:
        return jsonify({'error': '没有选择要导出的项目'}), 400

    try:
        # 创建内存中的 ZIP 文件
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for item in items:
                image_path = UPLOAD_FOLDER / item['image_path']

                if not image_path.exists():
                    continue

                # 读取图像获取尺寸
                img = cv2.imread(str(image_path))
                img_height, img_width = img.shape[:2]

                # 构建 LabelMe 格式
                labelme_data = {
                    'version': '5.10.1',
                    'flags': {},
                    'shapes': [],
                    'imagePath': image_path.name,
                    'imageHeight': img_height,
                    'imageWidth': img_width
                }

                # 添加检测框
                for det in item['detections']:
                    x1, y1, x2, y2 = det['bbox']

                    labelme_data['shapes'].append({
                        'label': det.get('class_name', 'insulator'),
                        'points': [
                            [x1, y1],
                            [x2, y2]
                        ],
                        'group_id': None,
                        'shape_type': 'rectangle',
                        'flags': {},
                        'mask': None
                    })

                # 获取模型信息（如果有）
                model_info = item.get('model_info', {})
                model_suffix = ''
                if model_info.get('name'):
                    # 从模型名称中提取简短标识
                    model_name = model_info.get('name', '').lower()
                    model_suffix = '_' + model_name.replace(' ', '_').replace('(', '').replace(')', '')

                # 将 JSON 写入 ZIP（文件名包含模型标识）
                json_str = json.dumps(labelme_data, indent=2, ensure_ascii=False)
                zip_file.writestr(f"{image_path.stem}{model_suffix}.json", json_str)

        zip_buffer.seek(0)

        # 生成 ZIP 文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = f"batch_export_{timestamp}.zip"

        # 保存 ZIP 文件
        zip_path = OUTPUT_FOLDER / zip_filename
        with open(zip_path, 'wb') as f:
            f.write(zip_buffer.getvalue())

        return jsonify({
            'success': True,
            'filename': zip_filename,
            'download_url': f'/download/{zip_filename}',
            'count': len(items)
        })

    except Exception as e:
        return jsonify({'error': f'批量导出失败: {str(e)}'}), 500


@app.route('/download/<filename>')
def download_file(filename):
    """下载文件"""
    try:
        file_path = OUTPUT_FOLDER / filename
        if file_path.exists():
            return send_file(str(file_path), as_attachment=True)
        return jsonify({'error': '文件不存在'}), 404
    except Exception as e:
        return jsonify({'error': f'下载失败: {str(e)}'}), 500


@app.route('/api/delete_image', methods=['POST'])
def delete_image():
    """
    删除单张图片及其相关文件
    """
    data = request.json
    image_path = UPLOAD_FOLDER / data['image_path']

    try:
        if image_path.exists():
            image_path.unlink()  # 删除图片文件

        # 同时删除对应的JSON文件（如果存在）
        json_path = OUTPUT_FOLDER / f"{image_path.stem}.json"
        if json_path.exists():
            json_path.unlink()

        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'error': f'删除失败: {str(e)}'}), 500


@app.route('/api/batch_delete_images', methods=['POST'])
def batch_delete_images():
    """
    批量删除图片及其相关文件
    """
    data = request.json
    image_paths = data.get('image_paths', [])

    if not image_paths:
        return jsonify({'error': '没有选择要删除的项目'}), 400

    try:
        success_count = 0

        for path_str in image_paths:
            image_path = UPLOAD_FOLDER / path_str

            if image_path.exists():
                image_path.unlink()
                success_count += 1

            # 同时删除对应的JSON文件（如果存在）
            json_path = OUTPUT_FOLDER / f"{image_path.stem}.json"
            if json_path.exists():
                json_path.unlink()

        return jsonify({
            'success': True,
            'count': success_count
        })

    except Exception as e:
        return jsonify({'error': f'批量删除失败: {str(e)}'}), 500


if __name__ == '__main__':
    print("\n启动服务中...")
    print(f"服务地址: http://{HOST}:{PORT}")
    print("按 Ctrl+C 停止服务")
    print("\n")
    print("提示:")
    print("  - 生产模式: 先运行 'cd web_ui_vite && npm run build' 构建前端")
    print("  - 开发模式: 运行 'cd web_ui_vite && npm run dev' 启动 Vite 开发服务器")
    print("    然后 Vite 开发服务器会自动代理 API 请求到此后端")
    print("\n")

    # 启动 Flask 应用
    app.run(host=HOST, port=PORT, debug=DEBUG, threaded=True)
