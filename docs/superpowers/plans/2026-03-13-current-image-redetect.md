# Current Image Redetect Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add current-image-only confidence/IoU re-detection from the settings panel and abnormal-priority overlap suppression.

**Architecture:** Extend the existing viewer settings panel to emit re-detect requests and keep `App.vue` responsible for applying the refreshed result to the active state. Move overlap suppression into a pure Python helper so the backend rule can be tested independently from OpenCV and YOLO.

**Tech Stack:** Vue 3, Vite, Vitest, Flask, Python unittest

---

## Chunk 1: Tests First

### Task 1: Add failing tests

**Files:**
- Modify: `web_ui_vite/tests/canvas-viewer.test.js`
- Create: `tests/test_detection_processing.py`

- [ ] Write a failing Vitest case for the settings-panel re-detect event.
- [ ] Write a failing Python unittest case for abnormal-priority overlap suppression.
- [ ] Run both tests and confirm they fail for the expected reason.

## Chunk 2: Implement Frontend + Backend

### Task 2: Add pure overlap helper and backend route

**Files:**
- Create: `detection_processing.py`
- Modify: `app.py`

- [ ] Add IoU and abnormal-priority suppression helpers.
- [ ] Add reusable detection execution in `app.py`.
- [ ] Add `/api/redetect` and wire it to the helper.

### Task 3: Add settings-panel controls

**Files:**
- Modify: `web_ui_vite/src/components/CanvasViewer.vue`
- Modify: `web_ui_vite/src/App.vue`
- Modify: `web_ui_vite/src/api/index.js`

- [ ] Add confidence/IoU controls to the existing settings panel.
- [ ] Emit a current-image re-detect event.
- [ ] Update active frontend state in place after the API call.

## Chunk 3: Verification

### Task 4: Verify

**Files:**
- None

- [ ] Run `python -m unittest tests/test_detection_processing.py`.
- [ ] Run `npm test`.
- [ ] Run `npm run build`.
