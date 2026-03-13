# Two-Stage Insulator Training Design

## Goal

在不修改现有 [`train_bbox_yolo.ipynb`](/home/hujing/yolo-web-ui/train_bbox_yolo.ipynb) 的前提下，新增一套两阶段训练方案：

1. 第一阶段继续使用 YOLO 在整图中检测绝缘子实例。
2. 在 `web_ui` 中对检测结果进行人工校正，得到高质量实例框和类别标签。
3. 将校正后的实例标注离线裁剪成单个绝缘子 crop，生成分类数据集。
4. 使用新的分类训练文件训练第二阶段缺陷分类模型。

## Why This Design

当前的一阶段模型已经可以正确识别绝缘子个数，因此更合理的下一步不是继续把“数量检测”和“缺陷识别”揉在一起，而是拆成两个职责清晰的阶段：

- 第一阶段专注“找出每个绝缘子在哪里”
- 第二阶段专注“判断这个绝缘子是什么状态”

这样做的收益是：

- 训练目标更单一，模型更稳定
- 数据生产链路更贴合真实使用流程
- 后续扩展到更多缺陷类别时，不需要重做第一阶段

## Scope

这次设计覆盖三个子系统：

1. `web_ui` 的实例级人工校正能力
2. 离线分类数据集生成器
3. 第二阶段分类训练文件

这次设计明确不做：

- 修改现有 [`train_bbox_yolo.ipynb`](/home/hujing/yolo-web-ui/train_bbox_yolo.ipynb) 的一阶段训练逻辑
- 在本轮中实现完整的第二阶段推理回接 UI
- 引入复杂的数据平台、审核流或版本系统

## User Workflow

目标工作流如下：

1. 使用第一阶段 YOLO 模型在 `web_ui` 中对原图进行检测。
2. 在 `web_ui` 中对每个绝缘子实例进行校正：
   - 修改类别标签
   - 删除误检框
   - 补加漏检框
   - 拖动或缩放框位置
3. 导出“校正后的最终实例标注”。
4. 运行新的数据集生成文件，将每个实例裁剪成单独的分类样本。
5. 运行新的分类训练文件，训练第二阶段分类模型。

## Architecture

### 1. Web UI As Annotation Correction Layer

`web_ui` 不再只是检测结果查看器，还承担“实例校正器”的角色。它的输出不再只是展示，而是作为第二阶段训练数据的上游。

每个实例最终需要具备：

- `image_path`
- `bbox`
- `class_id`
- `class_name`

导出的标注必须反映“人工校正后的最终状态”，而不是最初检测结果。

### 2. Offline Crop Dataset Builder

新增独立文件：

- [`build_insulator_cls_dataset.py`](/home/hujing/yolo-web-ui/build_insulator_cls_dataset.py)

职责：

- 读取 `web_ui` 导出的实例标注
- 加载原图
- 根据 bbox 裁剪出单个绝缘子 crop
- 按类别写入分类数据集目录
- 输出数据集统计、错误样本、跳过原因

推荐输出目录：

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
```

### 3. Independent Classification Trainer

新增独立文件：

- [`train_insulator_classifier.py`](/home/hujing/yolo-web-ui/train_insulator_classifier.py)

职责：

- 读取第二阶段分类数据集
- 配置分类模型训练参数
- 训练并保存分类模型
- 输出实验记录与评估指标

初始实现推荐继续使用 Ultralytics 的 classification 训练能力，降低迁移成本。

## Data Rules

### Annotation Rules

`web_ui` 导出的最终实例标注应满足：

- bbox 使用最终校正位置
- 类别标签使用最终人工确认值
- 删除的框不导出
- 新补的框必须可以正常导出

### Crop Rules

裁剪时建议执行以下规则：

- 对 bbox 增加 5% 到 10% padding
- 裁剪边界限制在原图尺寸内
- 过滤过小样本，例如宽或高小于最小阈值
- 保存为统一格式，例如 `.jpg`

### Split Rules

数据集划分优先按“原图”而不是按“crop 实例”切分，以避免同一张原图的多个实例同时出现在训练集和验证集，造成数据泄漏。

## Error Handling

### In Web UI

- 没有类别时不允许导出
- 非法 bbox 不允许保存
- 新增框和拖动框后应立即反馈当前实例状态

### In Dataset Builder

- 原图不存在时记录并跳过
- bbox 越界时自动裁剪到合法范围
- 裁剪结果尺寸异常时记录并跳过
- 输出最终统计：
  - 总实例数
  - 每类实例数
  - 跳过数量
  - 跳过原因

### In Classifier Training

- 数据目录缺失时直接报错退出
- 某个类别样本为 0 时阻止启动训练
- 输出训练配置快照，便于复现

## File Plan

需要新增或扩展的核心文件：

- 新增 [`build_insulator_cls_dataset.py`](/home/hujing/yolo-web-ui/build_insulator_cls_dataset.py)
  负责实例裁剪和分类数据集生成
- 新增 [`train_insulator_classifier.py`](/home/hujing/yolo-web-ui/train_insulator_classifier.py)
  负责第二阶段分类训练
- 后续扩展 `web_ui` 相关组件与导出逻辑
  以支持补框、删框、拖框、改标签

## Testing Strategy

### Web UI

- 补框、删框、拖框、改标签的交互测试
- 导出结果包含最终实例标注的测试

### Dataset Builder

- bbox 裁剪正确性测试
- padding 和边界裁剪测试
- 数据集划分不泄漏测试

### Classifier Training

- 配置文件生成测试
- 数据目录检查测试
- 最小样本集 smoke test

## Recommendation

建议按以下顺序推进：

1. 先补齐 `web_ui` 的实例级校正能力
2. 再实现离线裁剪脚本
3. 再实现分类训练文件
4. 最后再考虑把第二阶段推理结果接回 UI

这样可以保证第二阶段训练建立在可信数据之上，而不是在不稳定标注链路上强行推进。
