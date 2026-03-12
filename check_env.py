#!/usr/bin/env python3
"""
环境检查脚本
验证所有依赖是否正确安装
"""

import sys
from pathlib import Path

print("=" * 60)
print("环境检查工具")
print("=" * 60)
print()

errors = []

# 检查 Python 版本
print(f"✓ Python 版本: {sys.version.split()[0]}")
if sys.version_info < (3, 8):
    errors.append("Python 版本过低，需要 3.8+")

# 检查依赖
dependencies = [
    ('flask', 'Flask'),
    ('cv2', 'opencv-python'),
    ('numpy', 'numpy'),
    ('ultralytics', 'ultralytics'),
]

print("\n检查依赖...")
for module, name in dependencies:
    try:
        __import__(module)
        print(f"✓ {name}")
    except ImportError:
        print(f"✗ {name} - 未安装")
        errors.append(name)

# 检查模型文件
print("\n检查模型文件...")
model_path = Path(__file__).parent.parent / 'experiments/20260206_141411_bbox_yolo11x_exp002_bs8_is960_gpu2/weights/best.pt'
if model_path.exists():
    print(f"✓ 模型文件: {model_path}")
else:
    print(f"✗ 模型文件不存在: {model_path}")
    errors.append("模型文件")

# 检查目录权限
print("\n检查目录权限...")
for dir_name in ['uploads', 'outputs', 'templates']:
    dir_path = Path(dir_name)
    if dir_name == 'templates':
        dir_path = Path(__file__).parent / dir_name

    if dir_path.exists():
        print(f"✓ {dir_name}/")
    else:
        print(f"! {dir_name}/ - 将自动创建")

print()
print("=" * 60)

if errors:
    print("发现以下问题:")
    for error in errors:
        print(f"  - {error}")
    print()
    print("请运行: pip install -r requirements.txt")
    sys.exit(1)
else:
    print("✓ 所有检查通过！可以运行:")
    print("  python3 app.py")
    print("  或")
    print("  ./run.sh")
    sys.exit(0)
