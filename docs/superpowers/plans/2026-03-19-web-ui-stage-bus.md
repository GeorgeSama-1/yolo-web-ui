# Web UI Stage Bus Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把中间工作区顶部改成清晰表达一阶段/二阶段结果归属的阶段总线。

**Architecture:** 保持现有数据流不变，只重排 `CanvasViewer.vue` 的工具条和状态条。通过源码级测试锁定关键阶段文案，确保结果归属清晰且未启用分类时有明确提示。

**Tech Stack:** Vue 3, Vite, Python unittest

---

## Chunk 1: Lock Expected Labels

### Task 1: Expand source-level expectations

**Files:**
- Modify: `tests/test_ui_information_architecture.py`

- [ ] **Step 1: Write the failing test**

增加对以下文案的断言：

- `流程总线`
- `阶段 1 检测`
- `阶段 2 分类`
- `未启用分类`

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests/test_ui_information_architecture.py -v`

- [ ] **Step 3: Write minimal implementation**

在 `CanvasViewer.vue` 中加入对应文案和结构。

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests/test_ui_information_architecture.py -v`

## Chunk 2: Rebuild Canvas Workspace Header

### Task 2: Reorganize toolbar and stage bus

**Files:**
- Modify: `web_ui_vite/src/components/CanvasViewer.vue`

- [ ] **Step 1: Keep toolbar action-focused**

保留缩放、适应窗口、补框和当前图片名，统一工具条科技风样式。

- [ ] **Step 2: Replace flat stat cards with stage bus**

重排为：

- 阶段 1 检测
- 阶段 2 分类
- 当前选中

- [ ] **Step 3: Add two-stage disabled fallback**

未启用分类模型时，二阶段区域仍显示，但内容为“未启用分类”。

- [ ] **Step 4: Keep delete-selected action near current selection**

仅在有选中项时显示删除按钮，并让其跟随当前选中区域。

## Chunk 3: Verify

### Task 3: Run source-level verification

**Files:**
- Verify: `tests/test_ui_information_architecture.py`
- Verify: `tests/test_two_stage_classification.py`
- Verify: `tests/test_notebooks.py`

- [ ] **Step 1: Run UI architecture test**

Run: `python3 -m unittest tests/test_ui_information_architecture.py -v`

- [ ] **Step 2: Run existing Python regression coverage**

Run: `python3 -m unittest tests/test_two_stage_classification.py tests/test_notebooks.py`

- [ ] **Step 3: Check patch hygiene**

Run: `git diff --check`
