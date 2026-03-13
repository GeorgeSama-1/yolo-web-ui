# Two-Stage Training Workflow

## Overview

当前项目已经支持两阶段绝缘子训练流程：

1. 第一阶段：整图 YOLO 检测绝缘子实例
2. 第二阶段：基于实例 crop 的分类模型，判断 `normal / abnormal` 或更细缺陷类别

第一阶段训练文件保持不变：

- [`train_bbox_yolo.ipynb`](/home/hujing/yolo-web-ui/train_bbox_yolo.ipynb)

第二阶段新增独立文件：

- [`build_insulator_cls_dataset.py`](/home/hujing/yolo-web-ui/training/build_insulator_cls_dataset.py)
- [`train_insulator_classifier.py`](/home/hujing/yolo-web-ui/training/train_insulator_classifier.py)

## Step 1A: Detect And Correct In Web UI

在 `web_ui` 中使用第一阶段模型跑检测，然后对实例结果做人工校正。

当前已支持的校正动作：

- 修改单个框的类别标签
- 删除误检框
- 补加新的框
- 拖动选中的框移动位置
- 用校正条调框宽和框高
- 用画布角点拖拽缩放选中的框

完成校正后，导出结果。

导出的 JSON 除了 LabelMe `shapes` 外，还会带：

```json
{
  "metadata": {
    "image_path": "...",
    "original_path": "...",
    "instances": [
      {
        "id": 1,
        "class_id": 0,
        "class_name": "normal",
        "bbox": [x1, y1, x2, y2],
        "confidence": 0.93
      }
    ]
  }
}
```

这部分 `metadata.instances` 是第二阶段数据集生成脚本的直接输入。

## Step 1B: Or Use An Existing LabelMe Dataset Directly

如果你已经有现成的标准 LabelMe 数据集，也可以直接跳过 `web_ui` 校正步骤。

适用条件：

- 每张原图都有对应的 `.json`
- 每个矩形框都对应单个绝缘子实例
- `label` 已经是 `normal` / `abnormal` 或其他你想训练的分类标签

脚本现在同时支持两种输入：

- `web_ui` 导出的 `metadata.instances`
- 标准 LabelMe 的 `shapes`

标准 LabelMe 目录示例：

```text
dataset/
  images/
    a.jpg
    b.jpg
  annotations/
    a.json
    b.json
```

## Step 2: Build Classification Dataset

假设：

- 标注 JSON 放在 `outputs/annotations/` 或你自己的 LabelMe `annotations/`
- 原始图片放在 `uploads/` 或你自己的 `images/`
- 目标分类数据集放在 `data/insulator_cls_dataset/`

执行：

```bash
python -m training.build_insulator_cls_dataset \
  --annotations-dir outputs/annotations \
  --source-images-dir uploads \
  --output-dir data/insulator_cls_dataset
```

可选参数：

```bash
python -m training.build_insulator_cls_dataset \
  --annotations-dir outputs/annotations \
  --source-images-dir uploads \
  --output-dir data/insulator_cls_dataset \
  --padding-ratio 0.08 \
  --min-crop-size 24
```

生成后的目录结构：

```text
data/insulator_cls_dataset/
  train/
    normal/
    abnormal/
  val/
    normal/
    abnormal/
  test/
    normal/
    abnormal/
  dataset_summary.json
```

## Step 3: Train The Second-Stage Classifier

执行：

```bash
python -m training.train_insulator_classifier \
  --dataset-dir data/insulator_cls_dataset \
  --experiment-root experiments_cls \
  --experiment-name insulator_cls_exp001 \
  --model-weights yolo11n-cls.pt \
  --epochs 100 \
  --imgsz 224 \
  --batch 32 \
  --device 0
```

输出内容：

- 分类模型训练结果
- 实验目录
- `classifier_experiment.json` 训练配置快照

## Recommended Working Order

推荐按这个顺序推进：

1. 二选一准备标注来源：
   - 用当前最佳的一阶段模型在 `web_ui` 中校正并导出
   - 或直接准备现成的标准 LabelMe 数据集
2. 运行 `python -m training.build_insulator_cls_dataset`
3. 检查 `dataset_summary.json` 和抽样 crop 质量
4. 再运行 `python -m training.train_insulator_classifier`

## Practical Tips

- 如果第二阶段目标是分类，不要偷懒直接用一阶段检测输出做训练，最好经过人工校正
- 如果你已经有质量可靠的 LabelMe 二分类框标注，可以直接拿来裁剪生成分类数据集
- 分类数据集切分应按原图稳定划分，避免同一张原图的 crop 同时进入 train 和 val
- 建议先从 `normal / abnormal` 二分类跑通，再考虑更细缺陷标签
- 如果 crop 太紧，优先调 `--padding-ratio`
- 如果小框很多被跳过，检查 `dataset_summary.json` 中的 `skip_reasons`
