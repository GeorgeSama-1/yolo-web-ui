# 快速启动指南

## 方法一：使用启动脚本（推荐）

```bash
cd /bwopt/MODELS/hj/VL/YOLO_SEGMENT/web_ui
./run.sh
```

## 方法二：手动启动

1. **安装依赖**
```bash
pip install -r requirements.txt
```

2. **启动服务**
```bash
python3 app.py
```

3. **访问界面**
```
http://localhost:5000
```

## 目录说明

```
web_ui/
├── app.py              # Flask 后端
├── config.py           # 配置文件
├── templates/          # HTML 模板
│   └── index.html     # 前端界面
├── uploads/            # 上传图片（自动创建）
├── outputs/            # 导出文件（自动创建）
├── requirements.txt    # Python 依赖
├── run.sh             # 启动脚本
└── README.md          # 详细说明
```

## 配置修改

编辑 `config.py` 文件可以修改：
- 模型路径
- 置信度阈值
- 服务端口
- 其他参数

## 常见问题

**Q: 如何修改置信度阈值？**
A: 编辑 `config.py` 中的 `CONFIDENCE_THRESHOLD = 0.8`

**Q: 如何使用 GPU？**
A: 编辑 `app.py`，注释掉 `os.environ['CUDA_VISIBLE_DEVICES'] = ''`

**Q: 端口被占用怎么办？**
A: 编辑 `config.py` 修改 `PORT = 5000`
