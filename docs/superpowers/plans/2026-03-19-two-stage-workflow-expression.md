# Two-Stage Workflow Expression Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 把右侧任务面板顶部改成可视化流程链路，清楚表达“检测模型 -> 绝缘子框 -> 分类模型 -> normal / abnormal”。

**Architecture:** 保持现有后端数据流不变，只增强 `SidebarControls.vue` 的展示层。通过源码级测试锁定关键链路文案和降级状态，再最小实现节点式流程卡。

**Tech Stack:** Vue 3, Vite, Python unittest

---

## Chunk 1: Lock Workflow Copy

### Task 1: Extend source-level expectations

**Files:**
- Modify: `tests/test_ui_information_architecture.py`

- [ ] **Step 1: Write the failing test**

增加以下断言：

- `流程链路`
- `绝缘子框`
- `normal / abnormal`

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests/test_ui_information_architecture.py -v`

- [ ] **Step 3: Write minimal implementation**

在 `SidebarControls.vue` 中加入流程链路区块。

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests/test_ui_information_architecture.py -v`

## Chunk 2: Build Workflow Chain

### Task 2: Add visual process chain to sidebar

**Files:**
- Modify: `web_ui_vite/src/components/SidebarControls.vue`
- Modify: `web_ui_vite/tests/sidebar-controls.test.js`

- [ ] **Step 1: Add workflow chain section**

增加四节点链路：

- 检测模型
- 绝缘子框
- 分类模型
- normal / abnormal

- [ ] **Step 2: Add enabled/disabled messaging**

分类模型未启用时，保留链路但显示等待分类。

- [ ] **Step 3: Align wording in existing sidebar test**

更新现有 vitest 源码中的期望文字，使之与一阶段/两阶段表达一致。

## Chunk 3: Verify

### Task 3: Run source-level verification

**Files:**
- Verify: `tests/test_ui_information_architecture.py`
- Verify: `tests/test_two_stage_classification.py`
- Verify: `tests/test_notebooks.py`

- [ ] **Step 1: Run UI architecture verification**

Run: `python3 -m unittest tests/test_ui_information_architecture.py -v`

- [ ] **Step 2: Run Python regressions**

Run: `python3 -m unittest tests/test_two_stage_classification.py tests/test_notebooks.py`

- [ ] **Step 3: Check patch hygiene**

Run: `git diff --check`
