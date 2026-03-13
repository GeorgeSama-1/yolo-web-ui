# Training Folder Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move training and dataset-building scripts into a dedicated `training/` folder while keeping the web app root focused on web-serving code.

**Architecture:** Create a lightweight `training` package, move the two training-related entrypoints into it, and update tests and docs to reference the new module paths. Keep the runtime behavior of the scripts unchanged.

**Tech Stack:** Python, unittest, project documentation

---

### Task 1: Move the training scripts into a dedicated package

**Files:**
- Create: `training/__init__.py`
- Create: `training/build_insulator_cls_dataset.py`
- Create: `training/train_insulator_classifier.py`
- Modify: `tests/test_build_insulator_cls_dataset.py`
- Modify: `tests/test_train_insulator_classifier.py`

- [ ] **Step 1: Update the tests to import from `training.*`**
- [ ] **Step 2: Run `python -m unittest tests/test_build_insulator_cls_dataset.py tests/test_train_insulator_classifier.py` and confirm failure**
- [ ] **Step 3: Create the `training/` package and move the two scripts into it**
- [ ] **Step 4: Re-run `python -m unittest tests/test_build_insulator_cls_dataset.py tests/test_train_insulator_classifier.py` and confirm pass**

### Task 2: Update documentation and command examples

**Files:**
- Modify: `README.md`
- Modify: `docs/two_stage_training.md`

- [ ] **Step 1: Replace root-level script paths with `training/` paths**
- [ ] **Step 2: Update command examples to `python -m training...`**

### Task 3: Verify the migration

**Files:**
- Verify only

- [ ] **Step 1: Run `python -m unittest tests/test_build_insulator_cls_dataset.py tests/test_train_insulator_classifier.py tests/test_export_naming.py`**
- [ ] **Step 2: Run `python -m py_compile training/build_insulator_cls_dataset.py training/train_insulator_classifier.py`**
- [ ] **Step 3: Commit**

