# Training Folder Design

## Goal

把训练和数据集构建相关的 Python 脚本从仓库根目录收进单独目录，减少 `web_ui` 项目根目录的杂乱感，同时不影响现有 Web 服务入口。

## Scope

本次只整理训练链路相关脚本：

- `build_insulator_cls_dataset.py`
- `train_insulator_classifier.py`

保留根目录中的 Web 服务和后端辅助文件不动，例如：

- `app.py`
- `detection_processing.py`
- `model_bootstrap.py`
- `model_metadata.py`
- `export_naming.py`

## Recommended Structure

新增目录：

```text
training/
  __init__.py
  build_insulator_cls_dataset.py
  train_insulator_classifier.py
```

这样做的原因：

- 训练相关逻辑被明确归档到一个职责单一的位置
- 不需要大范围改动 `app.py` 和前端
- 后续如果再加数据转换或训练脚本，也有明确落点

## Command Changes

原来的命令：

```bash
python build_insulator_cls_dataset.py ...
python train_insulator_classifier.py ...
```

统一改成模块方式：

```bash
python -m training.build_insulator_cls_dataset ...
python -m training.train_insulator_classifier ...
```

## Compatibility

- 脚本内部逻辑保持不变，主要是文件位置和导入路径更新
- 测试更新为从 `training.*` 导入
- README 和 `docs/two_stage_training.md` 同步更新命令和文件路径

## Verification

最少验证：

- `python -m unittest tests/test_build_insulator_cls_dataset.py tests/test_train_insulator_classifier.py`
- `python -m py_compile training/build_insulator_cls_dataset.py training/train_insulator_classifier.py`

