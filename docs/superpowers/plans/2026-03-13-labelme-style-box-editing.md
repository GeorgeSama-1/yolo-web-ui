# LabelMe-Style Box Editing Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Let users select, drag, and resize existing detection boxes directly on the canvas like a lightweight LabelMe editor.

**Architecture:** Keep the existing `CanvasViewer.vue` canvas-based rendering, but move pointer hit-testing to any visible detection box instead of only the selected overlay. Preserve the current `App.vue` and detection-state data flow, and add targeted front-end tests that prove first-click drag works on original boxes.

**Tech Stack:** Vue 3, Vite, Vitest

---

## Chunk 1: Direct box hit-testing

### Task 1: Cover first-click drag with tests

**Files:**
- Modify: `web_ui_vite/tests/canvas-viewer.test.js`

- [ ] **Step 1: Write the failing test**
  Add a test showing that pressing and dragging inside an unselected detection emits `detection-click` immediately and then emits `update-detection-bbox`.

- [ ] **Step 2: Run test to verify it fails**
  Run: `cd web_ui_vite && npm test -- --run tests/canvas-viewer.test.js`
  Expected: FAIL because current drag logic only works for already-selected boxes.

- [ ] **Step 3: Write minimal implementation**
  Update `CanvasViewer.vue` so `handleMouseDown()` hit-tests any visible detection, selects it, and starts dragging with that box's bbox snapshot.

- [ ] **Step 4: Run test to verify it passes**
  Run: `cd web_ui_vite && npm test -- --run tests/canvas-viewer.test.js`
  Expected: PASS

### Task 2: Keep canvas interactions consistent

**Files:**
- Modify: `web_ui_vite/src/components/CanvasViewer.vue`
- Test: `web_ui_vite/tests/canvas-viewer.test.js`

- [ ] **Step 1: Add a focused regression test**
  Add a test proving that clicking empty canvas space does not emit a drag update and still allows deselection behavior to remain stable.

- [ ] **Step 2: Run test to verify it fails or guards the target behavior**
  Run: `cd web_ui_vite && npm test -- --run tests/canvas-viewer.test.js`

- [ ] **Step 3: Implement the minimal fix**
  Introduce explicit hit-testing helpers and drag state that store the active detection id instead of relying on `selectedDetectionForEditing`.

- [ ] **Step 4: Run tests**
  Run: `cd web_ui_vite && npm test -- --run tests/canvas-viewer.test.js`

## Chunk 2: Verification

### Task 3: Run focused verification

**Files:**
- Verify only

- [ ] **Step 1: Front-end unit tests**
  Run: `cd web_ui_vite && npm test -- --run tests/canvas-viewer.test.js tests/app-helpers.test.js`

- [ ] **Step 2: Production build**
  Run: `cd web_ui_vite && npm run build`

- [ ] **Step 3: Commit**
  Run:
  ```bash
  git add docs/superpowers/plans/2026-03-13-labelme-style-box-editing.md web_ui_vite/src/components/CanvasViewer.vue web_ui_vite/tests/canvas-viewer.test.js
  git commit -m "Add labelme-style box editing"
  ```
