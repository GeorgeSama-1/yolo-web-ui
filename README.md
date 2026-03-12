# 绝缘子检测 Web UI

基于 YOLOv8 的绝缘子检测 Web 应用，支持批量上传、实时检测、批量导出等功能。

## 功能特性

- 📤 **批量上传**：支持多文件和文件夹上传
- 🔍 **实时检测**：YOLOv8 模型实时检测绝缘子
- 🎨 **交互式可视化**：缩放、拖拽查看检测结果
- 📊 **检测统计**：实时显示检测数量和置信度
- 💾 **批量导出**：支持导出 LabelMe 格式（JSON 和 ZIP）
- 📁 **历史记录**：自动保存检测历史，支持快速查看

## 目录结构

```
web_ui/
├── app.py              # Flask 后端服务
├── config.py           # 配置文件
├── templates/          # HTML 模板
│   └── index.html     # 前端界面
├── models/             # 模型文件（已包含）
│   ├── best.pt        # 训练好的权重
│   ├── args.yaml      # 训练参数
│   └── *.png          # 训练结果图
├── uploads/            # 上传图片目录（自动创建）
├── outputs/            # 导出文件目录（自动创建）
├── requirements.txt    # Python 依赖
├── run.sh             # 启动脚本
└── README.md          # 本文件
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置说明

编辑 `config.py` 文件可以修改：
- 模型路径（当前使用 `models/best.pt`）
- 置信度阈值（默认 0.8）
- 服务端口（默认 5000）
- 其他参数

## 运行服务

```bash
python app.py
```

服务启动后访问：`http://localhost:5000`

## 使用说明

1. **上传图片**
   - 点击"选择文件"或"选择文件夹"
   - 支持批量上传多张图片

2. **查看检测结果**
   - 自动进行绝缘子检测
   - 使用缩放工具查看细节
   - 拖拽图片平移查看

3. **批量导出**
   - 在历史记录或文件列表中勾选要导出的项目
   - 点击"批量导出"按钮
   - 自动下载 ZIP 包（包含所有 LabelMe JSON 文件）

## 技术栈

- **后端**：Flask + YOLOv8
- **前端**：原生 JavaScript + Canvas
- **模型**：YOLOv11x (yolo11x-exp002)
  - 位置：`models/best.pt`
  - mAP50: 98.89%
  - 置信度阈值: 0.8
- **导出格式**：LabelMe JSON

## 注意事项

- 默认使用 CPU 进行推理（稳定但较慢）
- 如需使用 GPU，请修改 `app.py` 中的相关配置
- 历史记录最多保存 20 条
- 单个文件最大 50MB

## 故障排除

### CUDA 内存错误
如果遇到 CUDA 内存错误，当前已默认使用 CPU 推理。

### 检测框不准确
可以在 `app.py` 中调整置信度阈值：
```python
MIN_CONFIDENCE = 0.8  # 调整此值（0-1之间）
```

## 作者

绝缘子检测系统 v1.0
