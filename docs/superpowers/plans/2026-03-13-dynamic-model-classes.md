# Dynamic Model Classes Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the Vite web UI display class labels directly from the currently selected model for single-class and multi-class models.

**Architecture:** Reuse the existing `/api/classes` flow and keep `useDetectionState` as the central store for model class metadata. Remove remaining hardcoded labels from the UI and add regression tests that prove the legend and class-name helpers follow the current model.

**Tech Stack:** Vue 3, Vite, Vitest, Flask backend

---

## Chunk 1: Tests First

### Task 1: Add failing tests for dynamic class display

**Files:**
- Modify: `web_ui_vite/tests/canvas-viewer.test.js`
- Modify: `web_ui_vite/tests/app-helpers.test.js`

- [ ] Write a failing test that proves the viewer settings legend should render the current model classes instead of hardcoded labels.
- [ ] Write a failing test that proves class-name fallback stays generic when a class id is missing.
- [ ] Run the targeted tests and confirm they fail for the expected reason.

## Chunk 2: Implementation

### Task 2: Make the viewer legend dynamic

**Files:**
- Modify: `web_ui_vite/src/components/CanvasViewer.vue`
- Modify: `web_ui_vite/src/composables/useDetectionState.js`

- [ ] Replace the hardcoded legend rows with a computed list from `modelClasses`.
- [ ] Keep color lookup consistent with the existing class-color map.
- [ ] Keep the fallback name format generic.

### Task 3: Clean up backend fallback assumptions

**Files:**
- Modify: `app.py`

- [ ] Replace hardcoded label fallbacks that assume `insulator` when a more generic current-model lookup is safer.
- [ ] Preserve current behavior for single-class models.

## Chunk 3: Verification

### Task 4: Verify behavior

**Files:**
- None

- [ ] Run the targeted tests.
- [ ] Run `npm run build`.
- [ ] Summarize remaining gaps if any environment limitation appears.
