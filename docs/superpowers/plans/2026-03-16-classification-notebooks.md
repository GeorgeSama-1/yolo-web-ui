# Classification Notebooks Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add two Jupyter notebooks that mirror the repo's existing notebook-driven workflow for second-stage dataset building and classifier training.

**Architecture:** Keep the tested Python logic in `training/` as the source of truth and build thin notebooks that import and call those functions in a step-by-step, editable format. Add a small regression test that validates the notebooks exist and are parseable JSON with expected references.

**Tech Stack:** Jupyter Notebook JSON, Python, unittest

---

### Task 1: Add notebook regression coverage

**Files:**
- Create: `tests/test_notebooks.py`

- [ ] **Step 1: Write a failing test that checks both new notebooks exist and are valid JSON**
- [ ] **Step 2: Run `python -m unittest tests/test_notebooks.py` and confirm failure**

### Task 2: Create the notebooks

**Files:**
- Create: `build_insulator_cls_dataset.ipynb`
- Create: `train_insulator_classifier.ipynb`

- [ ] **Step 1: Create a dataset-building notebook that imports `training.build_insulator_cls_dataset`**
- [ ] **Step 2: Create a classifier-training notebook that imports `training.train_insulator_classifier`**
- [ ] **Step 3: Re-run `python -m unittest tests/test_notebooks.py` and confirm pass**

### Task 3: Verify notebook JSON

**Files:**
- Verify only

- [ ] **Step 1: Run `python -m py_compile training/build_insulator_cls_dataset.py training/train_insulator_classifier.py`**
- [ ] **Step 2: Run `python - <<'PY' ...` to parse both notebooks as JSON**

