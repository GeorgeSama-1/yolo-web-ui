# 绝缘子检测与两阶段分类系统

基于 Flask + Vue 3 + Ultralytics 的绝缘子检测 Web UI，同时支持从“一阶段绝缘子检测”到“二阶段缺陷分类”的完整数据生产与训练流程。

## 当前能力

- 批量上传图片或文件夹进行检测
- 自动发现并切换不同实验目录下的模型
- 可视化查看检测框、数量和置信度
- 导出 LabelMe JSON
- 在 `web_ui` 中进行实例级校正：
  - 修改类别
  - 删除框
  - 补加框
  - 直接拖动原始框位置
  - 角点拖拽缩放
  - 宽高滑块微调
- 基于导出的实例标注离线生成二阶段分类数据集
- 直接从标准 LabelMe 矩形框标注离线生成二阶段分类数据集
- 使用 notebook 训练二阶段分类模型
- 提供 notebook 版本的数据集检查、数据集生成、分类训练与两阶段推理流程

## 目录结构

```text
yolo-web-ui/
├── app.py
├── model_bootstrap.py
├── model_metadata.py
├── detection_processing.py
├── offline_workspace/
│   ├── notebooks/
│   │   ├── train_bbox_yolo.ipynb
│   │   ├── build_insulator_cls_dataset.ipynb
│   │   ├── review_labelme_annotations.ipynb
│   │   ├── train_insulator_classifier.ipynb
│   │   └── run_two_stage_inference.ipynb
│   ├── datasets/
│   │   ├── data_annotated_2class/
│   │   ├── insulator_cls_dataset_standard/
│   │   └── insulator_cls_dataset_tight/
│   └── outputs/
├── uploads/
├── outputs/
├── tests/
├── docs/
│   └── two_stage_training.md
└── web_ui_vite/
    ├── src/
    ├── tests/
    └── dist/
```

## 安装依赖

### Python

```bash
python -m pip install -r requirements.txt
```

### Frontend

```bash
cd web_ui_vite
npm install
```

## 启动 Web UI

如果你要以生产方式运行当前前端：

```bash
cd web_ui_vite
npm run build

cd ..
python app.py
```

服务启动后访问：

```text
http://localhost:5000
```

注意：后端会直接读取 `web_ui_vite/dist`，所以只 `git pull` 不会自动更新前端页面，修改前端后必须重新执行一次 `npm run build`。

## 从零开始的推荐流程

如果你现在还没有绝缘子检测模型，推荐按下面的顺序推进。

### 第一步：先训练一阶段绝缘子检测模型

使用现有 notebook：

- [`train_bbox_yolo.ipynb`](/home/hujing/yolo-web-ui/offline_workspace/notebooks/train_bbox_yolo.ipynb)

目标是先得到一个能够稳定框出绝缘子实例的模型。  
如果你现在的数据是整图加绝缘子框标注，建议先做单类检测：

- `insulator`

这一步只解决“每个绝缘子在哪里”。

### 第二步：把一阶段模型接到 Web UI

将训练好的权重放到实验目录结构中，例如：

```text
experiments/<timestamp>_<experiment_name>/weights/best.pt
```

`app.py` 会自动扫描该目录并识别模型。

### 第三步：在 Web UI 中校正实例

使用一阶段模型先自动出框，然后在网页里修正：

- 误检框：删除
- 漏检框：补加
- 框偏移：直接拖动原始框，或拖动角点缩放
- 类别不对：改成 `normal / abnormal`

这一步的输出就是二阶段分类数据的标注来源。

当前标注交互接近轻量版 LabelMe：

- 单击原始框即可选中
- 按住框内部可直接拖动位置
- 拖动四角控制点可缩放框
- 点击 `+ 补加框` 后在画布上拖拽可新建框
- 点击空白区域可取消当前选中

### 第四步：导出校正后的标注

导出的 JSON 除了 LabelMe `shapes` 外，还会包含：

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

这个 `metadata.instances` 就是二阶段分类裁剪脚本的直接输入。

### 第五步：生成二阶段分类数据集

推荐直接使用 notebook：

- [`build_insulator_cls_dataset.ipynb`](/home/hujing/yolo-web-ui/offline_workspace/notebooks/build_insulator_cls_dataset.ipynb)
- [`review_labelme_annotations.ipynb`](/home/hujing/yolo-web-ui/offline_workspace/notebooks/review_labelme_annotations.ipynb)

这些 notebook 已经按 cell 拆好：

- 路径配置
- 标注回框检查
- standard 数据集生成
- tight 数据集生成
- summary 输出

如果你手头已经有标准 LabelMe 数据集，也可以直接使用同一个脚本。当前脚本同时支持：

- `web_ui` 导出的 `metadata.instances`
- 标准 LabelMe 的 `shapes`

标准 LabelMe 数据集的典型目录例如：

```text
dataset/
  images/
    a.jpg
    b.jpg
  annotations/
    a.json
    b.json
```

只要每个框都是单个绝缘子实例，且 `label` 是 `normal` / `abnormal`，就可以直接裁剪生成分类数据集。

输出目录类似：

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

### 第六步：训练二阶段分类模型

推荐直接使用 notebook：

- [`train_insulator_classifier.ipynb`](/home/hujing/yolo-web-ui/offline_workspace/notebooks/train_insulator_classifier.ipynb)
- [`run_two_stage_inference.ipynb`](/home/hujing/yolo-web-ui/offline_workspace/notebooks/run_two_stage_inference.ipynb)

这些 notebook 已经按 cell 拆好：

- 训练参数配置
- 数据集检查
- 训练配置生成
- metadata 写入
- 启动训练
- 单张图片两阶段推理

输出包括：

- 分类模型训练结果
- 实验输出目录
- `classifier_experiment.json` 配置快照

## 日常使用建议

- 先把一阶段检测模型训稳，再开始生产二阶段分类数据
- 不建议直接拿未经人工校正的一阶段输出去训练分类模型
- 如果你已经有高质量的 LabelMe 二分类框标注，可以直接跳过 `web_ui` 校正步骤，直接生成分类 crop
- 如果 crop 太紧，优先增加 `--padding-ratio`
- 如果小框经常被跳过，检查 `dataset_summary.json` 里的 `skip_reasons`
- 分类数据集最好按原图稳定切分，避免同一张原图的 crop 同时进入 train 和 val

## 相关文件

- 一阶段检测训练：
  - [`train_bbox_yolo.ipynb`](/home/hujing/yolo-web-ui/offline_workspace/notebooks/train_bbox_yolo.ipynb)
- 二阶段数据集生成：
  - [`build_insulator_cls_dataset.ipynb`](/home/hujing/yolo-web-ui/offline_workspace/notebooks/build_insulator_cls_dataset.ipynb)
  - [`review_labelme_annotations.ipynb`](/home/hujing/yolo-web-ui/offline_workspace/notebooks/review_labelme_annotations.ipynb)
- 二阶段分类训练：
  - [`train_insulator_classifier.ipynb`](/home/hujing/yolo-web-ui/offline_workspace/notebooks/train_insulator_classifier.ipynb)
  - [`run_two_stage_inference.ipynb`](/home/hujing/yolo-web-ui/offline_workspace/notebooks/run_two_stage_inference.ipynb)
- 两阶段详细说明：
  - [`docs/two_stage_training.md`](/home/hujing/yolo-web-ui/docs/two_stage_training.md)

## 验证命令

### Backend

```bash
python -m unittest tests/test_model_metadata.py \
  tests/test_detection_processing.py \
  tests/test_model_bootstrap.py \
  tests/test_notebooks.py
```

### Frontend

```bash
cd web_ui_vite
npm test
npm run build
```
