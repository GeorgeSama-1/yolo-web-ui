# 离线训练与数据目录重组设计

## 目标

把训练相关 notebook、标注数据、离线生成的数据集和检查输出从仓库根目录收拢到一个独立目录里，让项目根目录更像一个 `web_ui` 服务项目，而不是混合了离线训练工作区。

## 约束

- 不修改 `web_ui` 前端代码
- 不调整 Flask 服务入口和服务端辅助脚本的位置
- 不把 `models/` 实验结果目录并入新的离线工作目录
- 训练链路继续以 notebook 为主，不重新引入训练侧 `.py`

## 推荐方案

新增一个统一的离线工作目录：`offline_workspace/`。

目录结构：

```text
offline_workspace/
  notebooks/
    train_bbox_yolo.ipynb
    build_insulator_cls_dataset.ipynb
    review_labelme_annotations.ipynb
    train_insulator_classifier.ipynb
    run_two_stage_inference.ipynb
  datasets/
    data_annotated_2class/
    insulator_cls_dataset_standard/
    insulator_cls_dataset_tight/
  outputs/
    labelme_review/
    two_stage_inference/
```

根目录继续保留：

- `app.py`
- `web_ui_vite/`
- `templates/`
- `model_bootstrap.py`
- `model_metadata.py`
- `detection_processing.py`
- `export_naming.py`
- `models/`

## 路径策略

notebook 内默认路径统一切到 `offline_workspace/` 下：

- 标注源：`offline_workspace/datasets/...`
- 生成数据集：`offline_workspace/datasets/...`
- 检查输出：`offline_workspace/outputs/...`
- 两阶段推理输出：`offline_workspace/outputs/...`

这样 notebook 打开后就能看到一套完整、集中、可修改的离线路径。

## 文档策略

README 和 `docs/two_stage_training.md` 改成：

- 根目录是 Web UI / 服务端
- `offline_workspace/` 是训练与数据处理工作区
- 所有训练步骤优先从 `offline_workspace/notebooks/` 进入

## 风险与处理

### 路径失效

notebook 里的默认路径会失效，因此需要同步更新默认常量。

### 文档残留旧路径

README 和两阶段说明文档需要一起更新，否则用户会继续在根目录找 notebook 和数据。

### 大文件移动

数据目录是未跟踪的大文件目录，迁移时只做文件系统级移动，不尝试纳入 git。

## 验证

- notebook 文件都存在于 `offline_workspace/notebooks/`
- notebook JSON 解析通过
- `tests/test_notebooks.py` 通过
- README 与 `docs/two_stage_training.md` 不再把训练 notebook 指向根目录
