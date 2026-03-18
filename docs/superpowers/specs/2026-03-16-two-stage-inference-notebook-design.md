# Two-Stage Inference Notebook Design

## Goal

新增一个可交互执行的 Jupyter notebook，用于对单张图片执行完整两阶段推理：

1. 用 YOLO 检测模型识别绝缘子数量与 bbox
2. 将 bbox 裁剪为实例 crop
3. 用 YOLO 分类模型对每个实例做 `normal / abnormal` 分类
4. 输出带框结果图、统计信息与异常实例列表

## User Experience

Notebook 应该像现有的 `train_bbox_yolo.ipynb` 一样按步骤拆成多个 cell，便于手动修改路径和参数。

用户可自定义：

- 检测模型路径
- 分类模型路径
- 输入图片路径
- 输出目录
- 检测阈值
- 裁剪 padding

## Output

Notebook 至少输出：

- 检测总数
- `normal` 数量
- `abnormal` 数量
- 异常实例明细
- 一张带 bbox 与分类标签的结果图
- 一个 `summary.json`
- 异常实例 crop 输出目录

## Technical Approach

直接在 notebook 中使用 Ultralytics：

- `YOLO(det_model_path)` 跑 detection
- `YOLO(cls_model_path)` 跑 classification

中间裁剪逻辑放在 notebook code cells 里完成，避免用户必须额外切换到 `.py` 脚本。

## Validation

- 新 notebook 文件存在并能被 JSON 解析
- notebook 内容明确引用 `ultralytics` 与两阶段推理关键步骤

