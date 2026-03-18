# Two-Stage Inference Notebook Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a notebook that runs single-image two-stage inference with a YOLO detector and YOLO classifier.

**Architecture:** Create one self-contained notebook with editable parameter cells, Ultralytics model loading, bbox rendering, crop classification, and summary export. Add a regression test that validates the notebook exists and includes expected two-stage inference references.

**Tech Stack:** Jupyter Notebook JSON, Python, Ultralytics

---

### Task 1: Add notebook regression coverage

**Files:**
- Modify: `tests/test_notebooks.py`

- [ ] **Step 1: Add a failing test for `run_two_stage_inference.ipynb`**
- [ ] **Step 2: Run `python -m unittest tests/test_notebooks.py` and confirm failure**

### Task 2: Create the notebook

**Files:**
- Create: `run_two_stage_inference.ipynb`

- [ ] **Step 1: Add parameter cells for model/image/output paths**
- [ ] **Step 2: Add detection, crop, classification, visualization, and summary cells**
- [ ] **Step 3: Re-run `python -m unittest tests/test_notebooks.py` and confirm pass**

### Task 3: Verify notebook JSON

**Files:**
- Verify only

- [ ] **Step 1: Parse the notebook JSON with Python**

