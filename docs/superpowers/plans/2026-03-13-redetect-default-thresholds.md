# Redetect Default Threshold Reset Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a reset-to-default action for the current-image redetect thresholds in the settings panel.

**Architecture:** Keep the change fully local to the viewer settings panel by resetting the existing reactive confidence and IoU values to their defaults. Cover the behavior with a focused component test.

**Tech Stack:** Vue 3, Vitest, Vue Test Utils

---

## Chunk 1: Test First

### Task 1: Add a failing component test

**Files:**
- Modify: `web_ui_vite/tests/canvas-viewer.test.js`

- [ ] Add a failing test for the reset-to-default action.
- [ ] Run the targeted test and confirm it fails first.

## Chunk 2: Implementation

### Task 2: Add the reset control

**Files:**
- Modify: `web_ui_vite/src/components/CanvasViewer.vue`

- [ ] Add the reset button.
- [ ] Reset the local thresholds to `0.80` and `0.30`.
- [ ] Ensure no re-detect event is emitted by the reset action.

## Chunk 3: Verification

### Task 3: Verify

**Files:**
- None

- [ ] Run the targeted viewer test.
- [ ] Run `npm test`.
