#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask + YOLOv8 绝缘子检测 Web 应用
支持 Canvas 交互式可视化和实时参数调整
支持检测框显示、选中和删除功能

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
from urllib.parse import quote
import os
import sys

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
    BASE_DIR = Path(__file__).parent
    MODEL_PATH = BASE_DIR / 'experiments/20260210_092222_bbox_yolo11x_exp003_bs8_is1280_gpu2_datav2/weights/best.pt'
    CONFIDENCE_THRESHOLD = 0.8
    UPLOAD_FOLDER = WEB_UI_DIR / 'uploads'
    OUTPUT_FOLDER = WEB_UI_DIR / 'outputs'
    HOST = '0.0.0.0'
    PORT = 5000
    DEBUG = True
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024
    MAX_HISTORY = 20

# ==================== NMS 辅助函数 ====================

def calculate_iou(box1, box2):
    """
    计算两个边界框的IoU（交并比）

    Args:
        box1, box2: [x1, y1, x2, y2] 格式的边界框

    Returns:
        IoU值 (0-1之间)
    """
    x1_min, y1_min, x1_max, y1_max = box1
    x2_min, y2_min, x2_max, y2_max = box2

    # 计算交集区域
    inter_x_min = max(x1_min, x2_min)
    inter_y_min = max(y1_min, y2_min)
    inter_x_max = min(x1_max, x2_max)
    inter_y_max = min(y1_max, y2_max)

    # 如果没有交集
    if inter_x_max < inter_x_min or inter_y_max < inter_y_min:
        return 0.0

    # 计算交集面积
    inter_area = (inter_x_max - inter_x_min) * (inter_y_max - inter_y_min)

    # 计算并集面积
    box1_area = (x1_max - x1_min) * (y1_max - y1_min)
    box2_area = (x2_max - x2_min) * (y2_max - y2_min)
    union_area = box1_area + box2_area - inter_area

    # 计算IoU
    iou = inter_area / union_area if union_area > 0 else 0.0
    return iou


def apply_custom_nms(detections, iou_threshold=0.5):
    """
    应用自定义NMS去除高度重叠的检测框

    **重要规则**：
    - 不管类别是否相同，只要检测框重叠度高（IoU > threshold），就只保留置信度最高的
    - 红色框和绿色框不能重叠共存，重叠时取置信度高的
    - 支持单类别和多类别模型

    Args:
        detections: 检测框列表
        iou_threshold: IoU阈值，默认0.5（可以调整到0.4或0.3更严格）

    Returns:
        过滤后的检测框列表
    """
    if len(detections) == 0:
        return detections

    # 按置信度降序排序
    sorted_detections = sorted(detections, key=lambda x: x['confidence'], reverse=True)

    keep = []
    suppressed = set()

    print(f"🔍 开始NMS处理，共 {len(detections)} 个检测框，IoU阈值={iou_threshold}")

    for i, det_i in enumerate(sorted_detections):
        if i in suppressed:
            continue

        keep.append(det_i)

        # 检查与后续检测框的重叠（不管类别是否相同）
        for j in range(i + 1, len(sorted_detections)):
            if j in suppressed:
                continue

            det_j = sorted_detections[j]
            iou = calculate_iou(det_i['bbox'], det_j['bbox'])

            # 如果IoU超过阈值，抑制置信度较低的框（即使类别不同）
            if iou > iou_threshold:
                suppressed.add(j)
                print(f"  🗑️  抑制检测框 #{det_j['id']} ({det_j['class_name']}, conf={det_j['confidence']:.3f}) "
                      f"与检测框 #{det_i['id']} ({det_i['class_name']}, conf={det_i['confidence']:.3f}) "
                      f"IoU={iou:.3f}")

    # 重新编号
    for idx, det in enumerate(keep):
        det['id'] = idx + 1

    print(f"✅ NMS完成: {len(detections)} 个检测框 -> {len(keep)} 个检测框")
    return keep


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
    """
    parts = exp_name.split('_')

    info = {
        'timestamp': f"{parts[0]}_{parts[1]}",  # 日期时间
        'task': parts[2] if len(parts) > 2 else 'unknown',  # 任务类型 (bbox)
        'model': parts[3] if len(parts) > 3 else 'unknown',  # 模型名称 (yolo11x)
        'num_classes': None,  # 类别数量（从标记中提取）
    }

    # 解析其他参数
    for part in parts:
        if part.startswith('exp'):
            info['exp'] = part
        elif part.endswith('class'):
            # 提取类别数量（2class, 3class等）
            try:
                info['num_classes'] = int(part.replace('class', ''))
            except:
                pass
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
        num_classes = info.get('num_classes', None)

        # 生成唯一key和描述
        key = exp_name

        # 根据类别数量生成不同的名称
        if num_classes is not None:
            # 有明确的类别标记（2class, 3class等）
            class_label = f"{num_classes}类"
            name = f"{model_type} {class_label} ({data_version})"
        else:
            # 没有类别标记，假设是1类或旧模型
            name = f"{model_type} ({data_version})"

        if batch_size:
            name += f" | BS{batch_size}"
        if exp_num:
            name += f" | Exp{exp_num}"

        # 构建详细描述
        desc_parts = []
        if num_classes:
            desc_parts.append(f"{num_classes}类")
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
            'num_classes': num_classes,
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

def get_model_classes(model_obj):
    """
    从 YOLO 模型中提取类别信息
    返回类别字典 {class_id: class_name}
    """
    if model_obj is None:
        return {0: 'insulator'}  # 默认单类别

    try:
        # 尝试从模型中获取类别名称
        if hasattr(model_obj, 'names') and model_obj.names:
            # YOLOv8/v11 模型存储类别名称在 model.names 属性中
            return model_obj.names
        else:
            # 如果没有类别名称，返回默认
            return {0: 'insulator'}
    except Exception as e:
        print(f"Warning: 无法获取模型类别信息: {e}")
        return {0: 'insulator'}

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

    # 获取并打印类别信息
    classes = get_model_classes(model)
    num_classes = len(classes)

    print(f"模型加载完成: {model_info['name']}")
    print(f"路径: {model_path}")
    print(f"描述: {model_info['description']}")
    print(f"类别数量: {num_classes}")
    print(f"类别映射: {classes}")

    # 更新模型信息中的类别数据
    model_info['classes'] = classes
    model_info['num_classes'] = num_classes

    return model_info

# 初始化加载默认模型
load_model(current_model_key)

print("=" * 60)
print("绝缘子检测 Web UI (Vue 3 + Vite 版本)")
print("使用 GPU 6 进行推理")
print("=" * 60)
print("置信度阈值:", CONFIDENCE_THRESHOLD)
print("上传目录:", UPLOAD_FOLDER.absolute())
print("导出目录:", OUTPUT_FOLDER.absolute())
print("Vue 构建目录:", VUE_DIST_DIR.absolute())
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

        # 获取类别信息（如果已加载）
        classes = info.get('classes', {})
        num_classes = info.get('num_classes', len(classes) if classes else 1)

        models_list.append({
            'key': key,
            'name': info['name'],
            'description': info['description'],
            'exists': exists,
            'exp_name': info.get('exp_name', key),
            'num_classes': num_classes,
            'classes': classes
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
        return jsonify({'error': f'未知的模型: {model_key}'}), 404

    try:
        model_info = load_model(model_key)
        return jsonify({
            'success': True,
            'model_key': model_key,
            'model_name': model_info['name'],
            'description': model_info['description'],
            'num_classes': model_info.get('num_classes', 1),
            'classes': model_info.get('classes', {0: 'insulator'})
        })
    except FileNotFoundError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': f'模型加载失败: {str(e)}'}), 500


@app.route('/api/classes', methods=['GET'])
def get_classes():
    """获取当前模型的类别信息"""
    try:
        classes = get_model_classes(model)
        model_info = AVAILABLE_MODELS.get(current_model_key, {})

        return jsonify({
            'success': True,
            'classes': classes,
            'num_classes': len(classes),
            'model_key': current_model_key,
            'model_name': model_info.get('name', 'Unknown')
        })
    except Exception as e:
        return jsonify({'error': f'获取类别信息失败: {str(e)}'}), 500


@app.route('/api/upload', methods=['POST'])
def upload_image():
    """
    处理图片上传和 YOLO 推理
    返回原始图片（不带框）+ 检测框坐标
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
        original_path = request.form.get('original_path', file.filename)

        # 尝试：打印收到的原始路径
        print(f"📁 上传文件: original_path='{original_path}', file.filename='{file.filename}'")

        # 生成保存的文件名（带时间戳前缀，替换路径分隔符避免目录问题）
        safe_filename = original_path.replace('/', '_').replace('\\', '_')
        filename = f"{timestamp}_{safe_filename}"
        image_path = UPLOAD_FOLDER / filename
        file.save(str(image_path))

        # Create a record file storing the original filename (e.g., DJI_0723_W.JPG)
        # This ensures we can recover the pure filename regardless of folder structure
        try:
            import os
            real_filename = os.path.basename(original_path)
            origin_record_path = UPLOAD_FOLDER / (filename + '.origin')
            with open(origin_record_path, 'w', encoding='utf-8') as f:
                f.write(real_filename)
            print(f"Created origin record: {real_filename}")
        except Exception as e:
            print(f"Warning: Could not save origin record: {e}")

        # 读取原图用于返回
        original_img = cv2.imread(str(image_path))

        # YOLO 推理 - 添加NMS参数去除重复检测
        # iou: IoU阈值用于NMS，默认0.7，降低此值可以更严格地去除重叠框
        # max_det: 最大检测数，防止过多误检
        results = model.predict(
            str(image_path),
            conf=0.25,
            iou=0.3,  # 降低IoU阈值到0.3，更严格地去除重叠检测框
            max_det=300,  # 限制最大检测数量
            verbose=False
        )
        result = results[0]

        # 获取模型类别信息
        model_classes = get_model_classes(model)

        # 提取检测框信息（不绘制到图片上）
        detections = []
        for box in result.boxes:
            xyxy = box.xyxy[0].cpu().numpy()
            x1, y1, x2, y2 = map(int, xyxy)
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])

            # 过滤低置信度检测框
            if conf < CONFIDENCE_THRESHOLD:
                continue

            # 从模型中获取真实的类别名称
            class_name = model_classes.get(cls_id, f'class_{cls_id}')

            detections.append({
                'id': len(detections) + 1,  # 重新编号
                'class_id': cls_id,
                'class_name': class_name,  # 使用真实类别名称
                'confidence': conf,
                'bbox': xyxy.tolist()  # [x1, y1, x2, y2] 边界框坐标
            })

        # 应用自定义NMS去除高度重叠的检测框（即使类别不同）
        if len(detections) > 0:
            print(f"\n📸 图片检测完成，共 {len(detections)} 个检测框，开始NMS处理...")
            detections = apply_custom_nms(detections, iou_threshold=0.3)  # 降低到0.3，更严格
            print(f"🎯 NMS后保留 {len(detections)} 个检测框\n")

        # 返回原图而不是绘制后的图片
        # 将原图转换为 base64 用于前端显示
        import base64
        _, buffer = cv2.imencode('.jpg', original_img)
        img_base64 = base64.b64encode(buffer).decode('utf-8')

        # 生成缩略图
        thumb_height = 150
        thumb_width = int(original_img.shape[1] * (thumb_height / original_img.shape[0]))
        thumbnail = cv2.resize(original_img, (thumb_width, thumb_height))
        _, thumb_buffer = cv2.imencode('.jpg', thumbnail, [cv2.IMWRITE_JPEG_QUALITY, 70])
        thumb_base64 = base64.b64encode(thumb_buffer).decode('utf-8')

        # 获取当前使用的模型信息
        model_info = AVAILABLE_MODELS.get(current_model_key, {})

        # 统计各类别的检测数量
        class_counts = {}
        for det in detections:
            class_name = det['class_name']
            class_counts[class_name] = class_counts.get(class_name, 0) + 1

        return jsonify({
            'success': True,
            'image_id': timestamp,
            'image_path': filename,
            'image_name': file.filename,  # 原始文件名（包含相对路径）
            'original_path': original_path,  # 原始相对路径（用于文件夹分组）
            'image_base64': img_base64,  # 原始图片（不带框）
            'thumbnail_base64': thumb_base64,
            'detections': detections,
            'total_count': len(detections),
            'class_counts': class_counts,  # 各类别统计
            'model_info': {
                'key': current_model_key,
                'name': model_info.get('name', 'Unknown'),
                'description': model_info.get('description', ''),
                'classes': model_classes,  # 添加类别映射
                'num_classes': len(model_classes)
            }
        })

    except Exception as e:
        return jsonify({'error': f'处理失败: {str(e)}'}), 500


@app.route('/api/reload_image', methods=['POST'])
def reload_image():
    """
    重新加载完整图片（用于按需加载）
    前端在查看历史记录时，如果图片不在内存中，调用此接口从服务器重新加载
    """
    try:
        data = request.get_json()
        if not data or 'image_path' not in data:
            return jsonify({'error': '缺少 image_path 参数'}), 400

        image_path = data['image_path']

        # 构建完整的文件路径
        full_path = UPLOAD_FOLDER / image_path

        if not full_path.exists():
            return jsonify({'error': f'图片文件不存在: {image_path}'}), 404

        # 读取图片
        img = cv2.imread(str(full_path))
        if img is None:
            return jsonify({'error': f'无法读取图片: {image_path}'}), 500

        # 转换为 base64
        import base64
        _, buffer = cv2.imencode('.jpg', img)
        img_base64 = base64.b64encode(buffer).decode('utf-8')

        return jsonify({
            'success': True,
            'image_base64': img_base64
        })

    except Exception as e:
        return jsonify({'error': f'加载失败: {str(e)}'}), 500


@app.route('/api/export_labelme', methods=['POST'])
def export_labelme():
    """
    导出 LabelMe 格式的 JSON 标注文件
    前端发送检测框数据，后端绘制并导出
    """
    data = request.json
    image_path = UPLOAD_FOLDER / data['image_path']

    if not image_path.exists():
        return jsonify({'error': '图像不存在'}), 404

    try:
        # 读取图像获取尺寸
        img = cv2.imread(str(image_path))
        img_height, img_width = img.shape[:2]

        # Get original filename for imagePath field in JSON
        # Priority: 1. Read .origin file -> 2. original_path from frontend -> 3. image_name -> 4. Fallback slice
        final_filename = None

        # Strategy 1: Try reading server-side .origin record file first
        import os
        origin_record_path = UPLOAD_FOLDER / (image_path.name + '.origin')
        if origin_record_path.exists():
            try:
                with open(origin_record_path, 'r', encoding='utf-8') as f:
                    final_filename = f.read().strip()
                    print(f"Read from origin record: {final_filename}")
            except Exception as e:
                print(f"Warning: Failed to read origin record: {e}")

        # Strategy 2: Try frontend parameters (backward compatibility)
        if not final_filename:
            if 'original_path' in data and data['original_path']:
                final_filename = os.path.basename(data['original_path'])
            elif 'image_name' in data and data['image_name']:
                final_filename = data['image_name']

        # Strategy 3: Fallback - remove first 16 chars (timestamp: YYYYMMDD_HHMMSS_)
        if not final_filename:
            server_filename = image_path.name
            if len(server_filename) > 16:
                final_filename = server_filename[16:]
            else:
                final_filename = server_filename

        # 构建 LabelMe 格式
        labelme_data = {
            'version': '5.10.1',
            'flags': {},
            'shapes': [],
            'imagePath': final_filename,
            'imageData': None,
            'imageHeight': img_height,
            'imageWidth': img_width
        }

        # 添加检测框（由前端传来的数据）
        for det in data['detections']:
            x1, y1, x2, y2 = det['bbox']
            labelme_data['shapes'].append({
                'label': det.get('class_name', 'insulator'),
                'points': [
                    [x1, y1],
                    [x2, y2]
                ],
                'group_id': None,
                'shape_type': 'rectangle',
                'flags': {}
            })

        # 打印调试信息
        print(f"导出信息: image_path={image_path.name}, 检测框数量={len(data['detections'])}")

        # 获取模型信息（如果有）
        model_info = data.get('model_info', {})

        # 从模型名称中提取简短标识
        model_suffix = ''
        if model_info.get('name'):
            # 使用URL安全的文件名
            model_name = model_info.get('name', '')
            # 移除空格、括号和特殊字符，用下划线替换
            safe_model_name = model_name.replace(' ', '_').replace('(', '').replace(')', '').replace('|', '_')
            model_suffix = '_' + safe_model_name

        # 保存 JSON 文件（使用带 model_suffix 的文件名）
        json_filename = f"{image_path.stem}{model_suffix}.json"
        json_path = OUTPUT_FOLDER / json_filename
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(labelme_data, f, indent=2, ensure_ascii=False)

        # 验证文件是否成功保存
        if not json_path.exists():
            print(f"错误: JSON文件保存失败: {json_path}")
            return jsonify({'error': 'JSON文件保存失败'}), 500

        file_size = json_path.stat().st_size
        print(f"JSON文件已保存: {json_path.name}, 大小: {file_size} bytes")

        # 从模型名称中提取简短标识
        model_suffix = ''
        if model_info.get('name'):
            # 使用URL安全的文件名（转为小写保持一致性）
            model_name = model_info.get('name', '').lower()
            # 移除空格、括号和特殊字符，用下划线替换
            safe_model_name = model_name.replace(' ', '_').replace('(', '').replace(')', '').replace('|', '_')
            model_suffix = '_' + safe_model_name

        json_filename = f"{image_path.stem}{model_suffix}.json"
        print(f"导出文件名: {json_filename}")

        # URL编码文件名以处理特殊字符（如#等）
        encoded_filename = quote(json_filename, safe='')

        return jsonify({
            'success': True,
            'json_path': json_path.name,
            'download_url': f'/download/{encoded_filename}'
        })

    except Exception as e:
        return jsonify({'error': f'导出失败: {str(e)}'}), 500


@app.route('/api/batch_export_labelme', methods=['POST'])
def batch_export_labelme():
    """
    批量导出 LabelMe 格式的 JSON 标注文件为 ZIP 包
    """
    data = request.json
    items = data.get('items', [])

    if not items:
        return jsonify({'error': '没有选择要导出的项目'}), 400

    try:
        # 创建内存中的 ZIP 文件
        import zipfile
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for item in items:
                image_path = UPLOAD_FOLDER / item['image_path']

                if not image_path.exists():
                    continue

                # 读取图像获取尺寸
                img = cv2.imread(str(image_path))
                img_height, img_width = img.shape[:2]

                # Get original filename for imagePath field in JSON
                # Priority: 1. Read .origin file -> 2. original_path from frontend -> 3. image_name -> 4. Fallback slice
                final_filename = None

                # Strategy 1: Try reading server-side .origin record file first
                import os
                origin_record_path = UPLOAD_FOLDER / (image_path.name + '.origin')
                if origin_record_path.exists():
                    try:
                        with open(origin_record_path, 'r', encoding='utf-8') as f:
                            final_filename = f.read().strip()
                    except Exception as e:
                        print(f"Warning: Failed to read origin record for {image_path.name}: {e}")

                # Strategy 2: Try frontend parameters (backward compatibility)
                if not final_filename:
                    if 'original_path' in item and item['original_path']:
                        final_filename = os.path.basename(item['original_path'])
                    elif 'image_name' in item and item['image_name']:
                        final_filename = item['image_name']

                # Strategy 3: Fallback - remove first 16 chars (timestamp: YYYYMMDD_HHMMSS_)
                if not final_filename:
                    server_filename = image_path.name
                    if len(server_filename) > 16:
                        final_filename = server_filename[16:]
                    else:
                        final_filename = server_filename

                # 构建 LabelMe 格式
                labelme_data = {
                    'version': '5.10.1',
                    'flags': {},
                    'shapes': [],
                    'imagePath': final_filename,
                    'imageData': None,
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
                        'flags': {}
                    })

                # 获取模型信息
                model_info = item.get('model_info', {})
                model_suffix = ''
                if model_info.get('name'):
                    # 使用URL安全的文件名
                    model_name = model_info.get('name', '').lower()
                    # 移除空格、括号和特殊字符，用下划线替换
                    safe_model_name = model_name.replace(' ', '_').replace('(', '').replace(')', '').replace('|', '_')
                    model_suffix = '_' + safe_model_name

                json_str = json.dumps(labelme_data, indent=2, ensure_ascii=False)
                zip_file.writestr(f"{image_path.stem}{model_suffix}.json", json_str)

        # 生成 ZIP 文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = f"batch_export_{timestamp}.zip"

        # 保存 ZIP 文件
        zip_path = OUTPUT_FOLDER / zip_filename
        with open(zip_path, 'wb') as f:
            f.write(zip_buffer.getvalue())

        # 验证和打印调试信息
        if zip_path.exists():
            file_size = zip_path.stat().st_size
            print(f"批量导出ZIP已保存: {zip_filename}, 大小: {file_size} bytes, 包含 {len(items)} 个文件")
        else:
            print(f"错误: ZIP文件保存失败: {zip_filename}")

        return jsonify({
            'success': True,
            'filename': zip_filename,
            'download_url': f'/download/{quote(zip_filename, safe="")}',
            'count': len(items)
        })

    except Exception as e:
        return jsonify({'error': f'批量导出失败: {str(e)}'}), 500


@app.route('/api/delete_image', methods=['POST'])
def delete_image():
    """
    删除单张图片及其相关文件
    """
    data = request.json
    image_path = UPLOAD_FOLDER / data['image_path']

    try:
        if image_path.exists():
            image_path.unlink()

            # Delete origin record file if exists
            origin_record_path = UPLOAD_FOLDER / (image_path.name + '.origin')
            if origin_record_path.exists():
                origin_record_path.unlink()

            # 同时删除对应的JSON文件（如果存在）
            # 文件名可能包含 model_suffix，使用 glob 匹配所有可能的文件
            for json_file in OUTPUT_FOLDER.glob(f"{image_path.stem}*.json"):
                json_file.unlink()

            return jsonify({'success': True})
        else:
            return jsonify({'error': '文件不存在'}), 404

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

                # Delete origin record file if exists
                origin_record_path = UPLOAD_FOLDER / (image_path.name + '.origin')
                if origin_record_path.exists():
                    origin_record_path.unlink()

                # 同时删除对应的JSON文件
                # 文件名可能包含 model_suffix，使用 glob 匹配所有可能的文件
                for json_file in OUTPUT_FOLDER.glob(f"{image_path.stem}*.json"):
                    json_file.unlink()

                success_count += 1

        return jsonify({
            'success': True,
            'count': success_count
        })

    except Exception as e:
        return jsonify({'error': f'批量删除失败: {str(e)}'}), 500


@app.route('/api/clear_all_uploads', methods=['POST'])
def clear_all_uploads():
    """
    清空 uploads 文件夹中的所有文件
    同时清理 outputs 文件夹中的所有 JSON 文件
    """
    try:
        upload_count = 0
        output_count = 0

        # Clear all files in uploads folder (including .origin files)
        for file in UPLOAD_FOLDER.iterdir():
            if file.is_file():
                file.unlink()
                upload_count += 1

        # Clear all JSON files in outputs folder
        for file in OUTPUT_FOLDER.iterdir():
            if file.is_file() and file.suffix == '.json':
                file.unlink()
                output_count += 1

        return jsonify({
            'success': True,
            'upload_count': upload_count,
            'output_count': output_count
        })

    except Exception as e:
        return jsonify({'error': f'清空失败: {str(e)}'}), 500


@app.route('/api/delete_detection', methods=['POST'])
def delete_detection():
    """
    删除指定图片的某个检测框
    前端发送: {image_path, detection_id}
    """
    data = request.json
    image_path = UPLOAD_FOLDER / data['image_path']
    detection_id = data.get('detection_id')

    if not image_path.exists():
        return jsonify({'error': '图片文件不存在'}), 404

    try:
        # 读取对应的 JSON 文件
        # 文件名可能包含 model_suffix，使用 glob 查找第一个匹配的文件
        matching_files = list(OUTPUT_FOLDER.glob(f"{image_path.stem}*.json"))
        if not matching_files:
            return jsonify({'error': 'JSON 文件不存在'}), 404

        json_path = matching_files[0]

        import json
        with open(json_path, 'r', encoding='utf-8') as f:
            labelme_data = json.load(f)

        # 查找并删除指定的检测框
        detections = labelme_data.get('shapes', [])
        original_count = len(detections)

        # 检查是否存在指定ID的检测框
        target_exists = any(d.get('id', -1) == detection_id for d in detections)

        if not target_exists:
            return jsonify({'error': '未找到指定的检测框'}), 404

        # 过滤检测框（排除要删除的）
        filtered_detections = [d for d in detections if d.get('id', -1) != detection_id]

        # 更新检测框列表
        labelme_data['shapes'] = filtered_detections

        # 重新编号检测框
        for i, det in enumerate(labelme_data['shapes']):
            det['id'] = i + 1

        # 保存更新后的 JSON
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(labelme_data, f, indent=2, ensure_ascii=False)

        return jsonify({
            'success': True,
            'remaining_count': len(labelme_data['shapes']),
            'deleted_count': 1
        })

    except Exception as e:
        return jsonify({'error': f'删除检测框失败: {str(e)}'}), 500


@app.route('/download/<path:filename>')
def download_file(filename):
    """下载文件"""
    from urllib.parse import unquote

    try:
        # URL解码文件名
        decoded_filename = unquote(filename)
        file_path = OUTPUT_FOLDER / decoded_filename

        if file_path.exists():
            return send_file(
                str(file_path),
                as_attachment=True,
                download_name=decoded_filename,
                mimetype='application/json'
            )
        else:
            print(f"文件不存在: {decoded_filename}")
            return jsonify({'error': '文件不存在'}), 404
    except Exception as e:
        print(f"下载失败: {str(e)}")
        return jsonify({'error': f'下载失败: {str(e)}'}), 500


# ==================== SPA 路由 (放在所有 API 路由之后，作为兜底路由) ====================

@app.route('/<path:path>')
def serve_spa(path):
    """
    SPA 路由支持 - 所有非 API 和非 download 请求都返回 index.html
    必须放在文件最后，让 Flask 先匹配具体的 API 和 download 路由
    这样 Vue Router 可以处理前端路由
    """
    # 跳过 API 和 download 请求（理论上不应该走到这里，因为前面有更具体的路由）
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


# ==================== 启动服务 ====================

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
