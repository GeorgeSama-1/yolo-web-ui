# UI Reorganization Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reorganize the UI so the right sidebar becomes the main action surface and the settings popup becomes style-only.

**Architecture:** Keep the existing three-panel layout, but move model switching, re-detect controls, and destructive data management out of the viewer popup and into `SidebarControls.vue`. `CanvasViewer.vue` keeps only direct image interaction and style settings.

**Tech Stack:** Vue 3, Vite, Vitest, Vue Test Utils

---

## Chunk 1: Tests First

### Task 1: Add failing sidebar workflow tests

**Files:**
- Modify: `web_ui_vite/tests/sidebar-controls.test.js`
- Modify: `web_ui_vite/tests/canvas-viewer.test.js`

- [ ] Add a failing test for the right sidebar re-detect controls.
- [ ] Add a failing test proving the viewer popup no longer contains task controls.
- [ ] Run the targeted tests and confirm they fail first.

## Chunk 2: Implementation

### Task 2: Reorganize the right sidebar

**Files:**
- Modify: `web_ui_vite/src/components/SidebarControls.vue`
- Modify: `web_ui_vite/src/App.vue`

- [ ] Move current-task actions into the right sidebar.
- [ ] Wire events for model switching, redetect, and clear-all-files.
- [ ] Keep upload/export behaviors intact.

### Task 3: Slim the settings popup

**Files:**
- Modify: `web_ui_vite/src/components/CanvasViewer.vue`

- [ ] Remove non-style task controls from the popup.
- [ ] Keep only appearance-related settings.

## Chunk 3: Verification

### Task 4: Verify

**Files:**
- None

- [ ] Run `npm test`.
- [ ] Run `npm run build`.
