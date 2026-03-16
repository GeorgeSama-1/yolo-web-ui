# Two-Stage Training Workflow

## Overview

当前项目已经支持两阶段绝缘子训练流程：

1. 第一阶段：整图 YOLO 检测绝缘子实例
2. 第二阶段：基于实例 crop 的分类模型，判断 `normal / abnormal` 或更细缺陷类别

第一阶段训练文件保持不变：

- [`train_bbox_yolo.ipynb`](/home/hujing/yolo-web-ui/offline_workspace/notebooks/train_bbox_yolo.ipynb)

第二阶段统一使用 notebook：

- [`build_insulator_cls_dataset.ipynb`](/home/hujing/yolo-web-ui/offline_workspace/notebooks/build_insulator_cls_dataset.ipynb)
- [`review_labelme_annotations.ipynb`](/home/hujing/yolo-web-ui/offline_workspace/notebooks/review_labelme_annotations.ipynb)
- [`train_insulator_classifier.ipynb`](/home/hujing/yolo-web-ui/offline_workspace/notebooks/train_insulator_classifier.ipynb)
- [`run_two_stage_inference.ipynb`](/home/hujing/yolo-web-ui/offline_workspace/notebooks/run_two_stage_inference.ipynb)

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

这部分 `metadata.instances` 是第二阶段数据集生成 notebook 的直接输入。

## Step 1B: Or Use An Existing LabelMe Dataset Directly

如果你已经有现成的标准 LabelMe 数据集，也可以直接跳过 `web_ui` 校正步骤。

适用条件：

- 每张原图都有对应的 `.json`
- 每个矩形框都对应单个绝缘子实例
- `label` 已经是 `normal` / `abnormal` 或其他你想训练的分类标签

数据集生成 notebook 现在同时支持两种输入：

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
- 目标分类数据集放在 `offline_workspace/datasets/insulator_cls_dataset_tight/`

打开 [`build_insulator_cls_dataset.ipynb`](/home/hujing/yolo-web-ui/offline_workspace/notebooks/build_insulator_cls_dataset.ipynb)，按顺序执行：

1. 配置 `ANNOTATIONS_DIR`
2. 配置 `SOURCE_IMAGES_DIR`
3. 配置 `STANDARD_OUTPUT_DIR` 和 `TIGHT_OUTPUT_DIR`
4. 运行 standard 数据集生成
5. 运行 tight 数据集生成

如果你想先检查标注质量，再打开：

- [`review_labelme_annotations.ipynb`](/home/hujing/yolo-web-ui/offline_workspace/notebooks/review_labelme_annotations.ipynb)

生成后的目录结构：

```text
offline_workspace/datasets/insulator_cls_dataset_tight/
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

打开 [`train_insulator_classifier.ipynb`](/home/hujing/yolo-web-ui/offline_workspace/notebooks/train_insulator_classifier.ipynb)，按顺序执行：

1. 配置 `DATASET_DIR`
2. 配置 `EXPERIMENT_ROOT`
3. 配置 `EXPERIMENT_NAME`
4. 配置 `MODEL_WEIGHTS`
5. 运行数据集检查
6. 运行训练

如果你要对单张图片执行完整两阶段推理，打开：

- [`run_two_stage_inference.ipynb`](/home/hujing/yolo-web-ui/offline_workspace/notebooks/run_two_stage_inference.ipynb)

输出内容：

- 分类模型训练结果
- 实验目录
- `classifier_experiment.json` 训练配置快照

## Recommended Working Order

推荐按这个顺序推进：

1. 二选一准备标注来源：
   - 用当前最佳的一阶段模型在 `web_ui` 中校正并导出
   - 或直接准备现成的标准 LabelMe 数据集
2. 运行 `build_insulator_cls_dataset.ipynb`
3. 检查 `dataset_summary.json` 和抽样 crop 质量
4. 再运行 `train_insulator_classifier.ipynb`

## Practical Tips

- 如果第二阶段目标是分类，不要偷懒直接用一阶段检测输出做训练，最好经过人工校正
- 如果你已经有质量可靠的 LabelMe 二分类框标注，可以直接拿来裁剪生成分类数据集
- 分类数据集切分应按原图稳定划分，避免同一张原图的 crop 同时进入 train 和 val
- 建议先从 `normal / abnormal` 二分类跑通，再考虑更细缺陷标签
- 如果 crop 太紧，优先调 `--padding-ratio`
- 如果小框很多被跳过，检查 `dataset_summary.json` 中的 `skip_reasons`
