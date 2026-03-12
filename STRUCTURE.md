# 📁 Web UI 文件夹

完整打包的绝缘子检测 Web 应用，包含所有必要文件。

## 📂 目录结构

```
web_ui/
│
├── 🔧 核心文件
│   ├── app.py                 # Flask 后端服务
│   ├── config.py              # 配置文件（模型路径、置信度等）
│   └── requirements.txt       # Python 依赖列表
│
├── 🎨 前端文件
│   └── templates/
│       └── index.html         # 主界面（含批量上传、缩放、导出）
│
├── 🤖 模型文件
│   └── models/
│       ├── best.pt            # YOLOv11x 权重（92.9MB）
│       ├── args.yaml          # 训练参数
│       ├── README_EXPERIMENT.md  # 实验记录
│       ├── results.png        # 训练结果图
│       ├── confusion_matrix.png
│       └── *.png               # 其他结果图
│
├── 📝 文档
│   ├── README.md              # 详细说明文档
│   ├── QUICKSTART.md          # 快速启动指南
│   └── .gitignore             # Git 忽略文件
│
├── 🚀 脚本工具
│   ├── run.sh                 # 启动脚本（推荐）
│   └── check_env.py           # 环境检查脚本
│
└── 📂 运行时目录（自动创建）
    ├── uploads/                # 上传的图片
    └── outputs/                # 导出的 JSON 文件
```

## 🚀 快速启动

### 方法 1：使用启动脚本（推荐）

```bash
cd /bwopt/MODELS/hj/VL/YOLO_SEGMENT/web_ui
./run.sh
```

### 方法 2：手动启动

```bash
cd /bwopt/MODELS/hj/VL/YOLO_SEGMENT/web_ui

# 安装依赖
pip install -r requirements.txt

# 启动服务
python3 app.py
```

## ⚙️ 配置说明

编辑 `config.py` 修改配置：

```python
# 模型配置
MODEL_PATH = Path('models/best.pt')              # 模型路径
CONFIDENCE_THRESHOLD = 0.8                        # 置信度阈值

# 服务器配置
HOST = '0.0.0.0'                                 # 监听地址
PORT = 5000                                      # 服务端口
DEBUG = True                                     # 调试模式

# 文件配置
MAX_CONTENT_LENGTH = 50 * 1024 * 1024            # 最大上传 50MB
MAX_HISTORY = 20                                 # 历史记录最多20条
```

## 🎯 功能特性

### 批量处理
- 📄 选择文件：支持多文件上传
- 📁 选择文件夹：一次上传整个文件夹
- 🔄 自动队列：依次处理所有图片
- 📊 实时统计：显示处理进度和结果

### 可视化
- 🔍 缩放：放大、缩小、适应窗口、实际尺寸
- 🖱️ 拖拽：鼠标拖拽平移图片
- 🎨 高对比度：红色边框 + 黄色半透明填充
- 📈 置信度显示：每个检测框显示置信度

### 导出功能
- 📥 当前结果：导出单张图片的 LabelMe JSON
- 📦 批量导出：选中多个结果，导出为 ZIP 包
- ✅ 格式标准：完全兼容 LabelMe 工具

### 历史记录
- 📁 自动保存：最多保存 20 条检测历史
- 🖼️ 缩略图：快速预览历史结果
- 🔄 快速加载：点击历史记录立即查看
- 📊 统计信息：显示绝缘子数量和置信度

## 📊 模型信息

- **模型**: YOLOv11x (yolo11x-exp002)
- **mAP50**: 98.89%
- **Precision**: 97.38%
- **Recall**: 96.97%
- **置信度阈值**: 0.8
- **输入尺寸**: 960x960

## ⚠️ 注意事项

1. **模型路径**：模型已包含在 `models/` 目录中
2. **CPU 推理**：默认使用 CPU（稳定但较慢）
3. **内存占用**：建议至少 8GB RAM
4. **历史记录**：最多保存 20 条，超出自动删除
5. **文件大小**：单个文件最大 50MB

## 🔧 故障排除

### 模型加载失败
```bash
# 检查模型文件是否存在
ls -lh models/best.pt
```

### 端口被占用
```python
# 编辑 config.py
PORT = 5001  # 修改为其他端口
```

### 依赖安装失败
```bash
# 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 检测结果不准确
```python
# 编辑 config.py，调整置信度阈值
CONFIDENCE_THRESHOLD = 0.9  # 提高阈值（更严格）
CONFIDENCE_THRESHOLD = 0.7  # 降低阈值（更宽松）
```

## 📞 技术支持

遇到问题请检查：
1. 运行 `python3 check_env.py` 检查环境
2. 查看控制台输出的错误信息
3. 确认模型文件存在且完整

## 📅 更新日志

- **v1.0** (2025-02-09)
  - ✅ 批量上传功能
  - ✅ 置信度过滤（0.8阈值）
  - ✅ 图片缩放和拖拽
  - ✅ 批量导出（ZIP格式）
  - ✅ 历史记录管理
  - ✅ 完整模型文件打包
