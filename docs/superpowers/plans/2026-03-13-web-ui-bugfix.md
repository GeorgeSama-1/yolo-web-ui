# Web UI Bugfix Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Repair the known runtime and state-consistency bugs in the Vite web UI without restructuring the app.

**Architecture:** Keep the existing Vue component/state setup and fix the broken interaction boundaries where component events, backend APIs, and cached image state currently disagree. Add small, focused test coverage around the repaired flows so the regressions stay pinned down.

**Tech Stack:** Vue 3, Vite, Vitest, Vue Test Utils

---

## Chunk 1: Test Harness And Regression Tests

### Task 1: Add frontend test tooling

**Files:**
- Modify: `web_ui_vite/package.json`
- Create: `web_ui_vite/vitest.config.js`
- Create: `web_ui_vite/tests/setup.js`

- [ ] Add Vitest + Vue test config.
- [ ] Add a `test` script.
- [ ] Verify the test runner starts.

### Task 2: Write failing regression tests

**Files:**
- Create: `web_ui_vite/tests/sidebar-controls.test.js`
- Create: `web_ui_vite/tests/canvas-viewer.test.js`
- Create: `web_ui_vite/tests/app-helpers.test.js`

- [ ] Write a failing test for the file-list clear action.
- [ ] Write a failing test for the declared hover event / emitted hover behavior.
- [ ] Write a failing test for comparison-image fallback and backend-backed detection deletion helper logic.
- [ ] Run the tests and confirm they fail for the expected reasons.

## Chunk 2: Implement The Fixes

### Task 3: Repair backend/API boundaries

**Files:**
- Modify: `web_ui_vite/src/api/index.js`
- Modify: `web_ui_vite/src/App.vue`

- [ ] Add missing API helper for clearing uploads.
- [ ] Route detection deletion through backend calls and keep frontend state in sync.
- [ ] Reload missing images before opening comparison panels.

### Task 4: Repair component/runtime issues

**Files:**
- Modify: `web_ui_vite/src/components/SidebarControls.vue`
- Modify: `web_ui_vite/src/components/CanvasViewer.vue`
- Modify: `web_ui_vite/src/composables/useDetectionState.js`

- [ ] Fix the file-list clear action so it no longer throws.
- [ ] Declare the hover event and remove stale state when clearing.
- [ ] Preserve intended clear-history vs clear-files behavior.

## Chunk 3: Verification

### Task 5: Run verification

**Files:**
- None

- [ ] Run targeted tests.
- [ ] Run `npm run build`.
- [ ] Review results and note any environment gaps if something cannot run.
