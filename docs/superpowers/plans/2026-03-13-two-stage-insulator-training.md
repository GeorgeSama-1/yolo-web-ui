# Two-Stage Insulator Training Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在不修改现有一阶段训练 notebook 的前提下，新增实例校正、分类数据集生成和第二阶段分类训练三段式流程。

**Architecture:** 维持第一阶段 YOLO 检测不变，将 `web_ui` 作为实例级校正层，再通过独立脚本离线生成 crop 分类数据集，最后由独立训练文件完成第二阶段分类训练。每个阶段单独可运行、可验证、可替换。

**Tech Stack:** Flask, Vue 3, Ultralytics YOLO, Python scripts, unittest / vitest

---

## Chunk 1: Web UI Instance Correction

### Task 1: Define exported instance schema

**Files:**
- Modify: `app.py`
- Modify: `web_ui_vite/src/api/index.js`
- Modify: `web_ui_vite/src/App.vue`
- Test: `web_ui_vite/tests/app-helpers.test.js`

- [ ] **Step 1: Write a failing frontend test for exporting corrected instance data**

- [ ] **Step 2: Run the targeted test and confirm the current export payload is insufficient**

- [ ] **Step 3: Extend export payload shape to include final bbox, class_id, class_name, image_path**

- [ ] **Step 4: Run the targeted test to verify export schema**

- [ ] **Step 5: Commit**

### Task 2: Add class editing for each detection

**Files:**
- Modify: `web_ui_vite/src/components/CanvasViewer.vue`
- Modify: `web_ui_vite/src/App.vue`
- Modify: `web_ui_vite/src/composables/useDetectionState.js`
- Test: `web_ui_vite/tests/canvas-viewer.test.js`

- [ ] **Step 1: Write a failing test for changing a detection class label**

- [ ] **Step 2: Run the test to verify failure**

- [ ] **Step 3: Add minimal UI and state flow for editing class label**

- [ ] **Step 4: Re-run the test and verify pass**

- [ ] **Step 5: Commit**

### Task 3: Support delete, add, and drag/resize box correction

**Files:**
- Modify: `web_ui_vite/src/components/CanvasViewer.vue`
- Modify: `web_ui_vite/src/App.vue`
- Modify: `web_ui_vite/src/composables/useDetectionState.js`
- Test: `web_ui_vite/tests/canvas-viewer.test.js`

- [ ] **Step 1: Write failing tests for deleting, adding, and moving a box**

- [ ] **Step 2: Run targeted tests and record current failures**

- [ ] **Step 3: Implement the smallest viable correction interaction flow**

- [ ] **Step 4: Re-run tests until pass**

- [ ] **Step 5: Commit**

## Chunk 2: Offline Classification Dataset Builder

### Task 4: Create crop dataset builder script

**Files:**
- Create: `build_insulator_cls_dataset.py`
- Create: `tests/test_build_insulator_cls_dataset.py`

- [ ] **Step 1: Write failing tests for bbox crop generation, padding, and split behavior**

- [ ] **Step 2: Run `python -m unittest tests/test_build_insulator_cls_dataset.py` and confirm failure**

- [ ] **Step 3: Implement crop extraction, padding, per-image split assignment, and class-folder output**

- [ ] **Step 4: Re-run the tests until pass**

- [ ] **Step 5: Commit**

### Task 5: Add dataset statistics and skip reporting

**Files:**
- Modify: `build_insulator_cls_dataset.py`
- Modify: `tests/test_build_insulator_cls_dataset.py`

- [ ] **Step 1: Write failing tests for stats summary and skipped-sample reporting**

- [ ] **Step 2: Run the targeted test and confirm failure**

- [ ] **Step 3: Implement summary JSON / console reporting**

- [ ] **Step 4: Re-run tests until pass**

- [ ] **Step 5: Commit**

## Chunk 3: Second-Stage Classification Trainer

### Task 6: Create standalone classifier training file

**Files:**
- Create: `train_insulator_classifier.py`
- Create: `tests/test_train_insulator_classifier.py`

- [ ] **Step 1: Write failing tests for dataset directory validation and config assembly**

- [ ] **Step 2: Run `python -m unittest tests/test_train_insulator_classifier.py` and confirm failure**

- [ ] **Step 3: Implement a minimal training entrypoint using Ultralytics classification**

- [ ] **Step 4: Re-run tests until pass**

- [ ] **Step 5: Commit**

### Task 7: Add experiment logging for classifier runs

**Files:**
- Modify: `train_insulator_classifier.py`
- Modify: `tests/test_train_insulator_classifier.py`

- [ ] **Step 1: Write a failing test for experiment metadata output**

- [ ] **Step 2: Run the test and confirm failure**

- [ ] **Step 3: Save run config, dataset stats, and output paths alongside training**

- [ ] **Step 4: Re-run tests until pass**

- [ ] **Step 5: Commit**

## Chunk 4: Integration and Verification

### Task 8: Add usage docs for the two-stage pipeline

**Files:**
- Modify: `README.md` or create `docs/two_stage_training.md`

- [ ] **Step 1: Document the end-to-end flow from UI correction to classifier training**

- [ ] **Step 2: Include exact commands and required input/output directories**

- [ ] **Step 3: Commit**

### Task 9: Run verification

**Files:**
- Modify: as needed based on failures

- [ ] **Step 1: Run backend unit tests**
Run: `python -m unittest tests/test_model_metadata.py tests/test_detection_processing.py tests/test_model_bootstrap.py`

- [ ] **Step 2: Run new dataset-builder and classifier tests**
Run: `python -m unittest tests/test_build_insulator_cls_dataset.py tests/test_train_insulator_classifier.py`

- [ ] **Step 3: Run frontend tests**
Run: `cd web_ui_vite && npm test`

- [ ] **Step 4: Run frontend build**
Run: `cd web_ui_vite && npm run build`

- [ ] **Step 5: Commit final fixes**
