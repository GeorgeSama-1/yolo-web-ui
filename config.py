#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web UI 配置文件
"""

import os
from pathlib import Path

# 当前目录（web_ui）
CURRENT_DIR = Path(__file__).parent
# 项目根目录
BASE_DIR = CURRENT_DIR.parent

# 模型配置（使用 web_ui 内的模型）
MODEL_PATH = CURRENT_DIR / 'models' / 'best_v2.pt'
CLASSIFICATION_MODEL_PATH = None
CONFIDENCE_THRESHOLD = 0  # 置信度阈值

# 目录配置（使用相对路径）
UPLOAD_FOLDER = CURRENT_DIR / 'uploads'
OUTPUT_FOLDER = CURRENT_DIR / 'outputs'

# 服务器配置
HOST = '0.0.0.0'
PORT = 5000
DEBUG = True

# 文件上传配置
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB

# 历史记录配置
MAX_HISTORY = 20  # 最多保存20条历史记录

# 缩略图配置
THUMBNAIL_HEIGHT = 150
THUMBNAIL_QUALITY = 70

# 图片配置
JPEG_QUALITY = 95  # 输出图片质量

# 导出配置
EXPORT_FORMAT = 'labelme'  # LabelMe JSON 格式
