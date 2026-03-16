# Offline Workspace Layout Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move offline datasets, notebooks, and offline outputs into a dedicated `offline_workspace/` directory while keeping Web UI and backend service files in place.

**Architecture:** Keep the repository root focused on the Flask service and Vue frontend, and create a separate offline workspace subtree for notebooks, datasets, and review/inference outputs. Update notebook default paths and documentation to point to the new layout without changing Web UI code paths.

**Tech Stack:** Python, Jupyter notebook JSON, filesystem moves, unittest, Markdown docs

---

## Chunk 1: Lock the expected layout with tests

### Task 1: Update notebook tests to expect the new workspace paths

**Files:**
- Modify: `tests/test_notebooks.py`

- [ ] **Step 1: Write the failing test**

Add assertions that:
- `offline_workspace/notebooks/build_insulator_cls_dataset.ipynb` exists
- `offline_workspace/notebooks/review_labelme_annotations.ipynb` exists
- `offline_workspace/notebooks/train_insulator_classifier.ipynb` exists
- `offline_workspace/notebooks/run_two_stage_inference.ipynb` exists
- the notebook source references `offline_workspace/`

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest tests/test_notebooks.py`
Expected: FAIL because notebooks still live in the root or still point at old paths

- [ ] **Step 3: Write minimal implementation**

Update `tests/test_notebooks.py` to read notebooks from `offline_workspace/notebooks`.

- [ ] **Step 4: Run test to verify it still reflects missing implementation**

Run: `python -m unittest tests/test_notebooks.py`
Expected: FAIL until the notebooks are moved and updated

## Chunk 2: Move notebooks and update defaults

### Task 2: Move notebook files into the offline workspace

**Files:**
- Create: `offline_workspace/notebooks/`
- Move: `build_insulator_cls_dataset.ipynb`
- Move: `review_labelme_annotations.ipynb`
- Move: `train_insulator_classifier.ipynb`
- Move: `run_two_stage_inference.ipynb`
- Move: `train_bbox_yolo.ipynb`

- [ ] **Step 1: Move notebook files**

Place all offline notebooks into `offline_workspace/notebooks/`.

- [ ] **Step 2: Update notebook test locations**

Make sure `tests/test_notebooks.py` points to the new notebook locations.

### Task 3: Update notebook default paths to the new workspace

**Files:**
- Modify: `offline_workspace/notebooks/build_insulator_cls_dataset.ipynb`
- Modify: `offline_workspace/notebooks/review_labelme_annotations.ipynb`
- Modify: `offline_workspace/notebooks/train_insulator_classifier.ipynb`
- Modify: `offline_workspace/notebooks/run_two_stage_inference.ipynb`

- [ ] **Step 1: Change dataset notebook defaults**

Use:
- `offline_workspace/datasets/data_annotated_2class`
- `offline_workspace/datasets/insulator_cls_dataset_standard`
- `offline_workspace/datasets/insulator_cls_dataset_tight`

- [ ] **Step 2: Change review notebook defaults**

Use:
- `offline_workspace/datasets/data_annotated_2class`
- `offline_workspace/outputs/labelme_review`

- [ ] **Step 3: Change classifier notebook defaults**

Use:
- `offline_workspace/datasets/insulator_cls_dataset_tight`
- `experiments_cls/` as training output root

- [ ] **Step 4: Change two-stage inference notebook defaults**

Use:
- `offline_workspace/outputs/two_stage_inference`

## Chunk 3: Move datasets and offline outputs

### Task 4: Create the offline workspace subdirectories

**Files:**
- Create: `offline_workspace/datasets/`
- Create: `offline_workspace/outputs/`

- [ ] **Step 1: Create destination directories**

Prepare directories for datasets and outputs.

### Task 5: Move existing offline data directories

**Files:**
- Move: `data_annotated_2class/` -> `offline_workspace/datasets/data_annotated_2class/`
- Move: `data/` -> `offline_workspace/datasets/`
- Move: `debug/labelme_review/` -> `offline_workspace/outputs/labelme_review/`
- Move: `debug/two_stage_inference/` -> `offline_workspace/outputs/two_stage_inference/`

- [ ] **Step 1: Move the annotated dataset**

Relocate the raw LabelMe dataset into the offline workspace.

- [ ] **Step 2: Move generated classification datasets**

Relocate `data/` contents under `offline_workspace/datasets/`.

- [ ] **Step 3: Move offline review and inference outputs if they exist**

Only move output directories that already exist.

## Chunk 4: Update documentation

### Task 6: Rewrite README around the offline workspace concept

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Update the project tree**

Show `offline_workspace/` and remove root-level offline notebook paths.

- [ ] **Step 2: Update all notebook references**

Point links to `offline_workspace/notebooks/...`.

- [ ] **Step 3: Update dataset paths in the examples**

Point examples to `offline_workspace/datasets/...`.

### Task 7: Update two-stage training documentation

**Files:**
- Modify: `docs/two_stage_training.md`

- [ ] **Step 1: Rewrite notebook references**

Point all notebook links to `offline_workspace/notebooks/...`.

- [ ] **Step 2: Rewrite path examples**

Point data and output paths to `offline_workspace/...`.

## Chunk 5: Verify

### Task 8: Run verification

**Files:**
- Verify: `tests/test_notebooks.py`

- [ ] **Step 1: Run notebook tests**

Run: `python -m unittest tests/test_notebooks.py`
Expected: PASS

- [ ] **Step 2: Parse notebook JSON files**

Run a Python snippet that loads all notebooks under `offline_workspace/notebooks/`.
Expected: all parse successfully

- [ ] **Step 3: Inspect git status**

Run: `git status --short`
Expected: only offline layout, docs, and test changes; no Web UI source changes
