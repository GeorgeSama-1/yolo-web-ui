# Web UI Information Architecture Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reorganize the Web UI into a clearer “upload -> inspect -> correct -> export” workflow and strengthen the sci-fi visual hierarchy without changing core detection behavior.

**Architecture:** Keep the existing three-panel application shell, but repurpose each panel around a single responsibility. Surface runtime state explicitly in the right rail, simplify the left rail into records + filters, and tighten the center workspace around active image correction.

**Tech Stack:** Vue 3, Vite, Tailwind utility classes, existing Flask backend metadata endpoints, Python unittest source-level guards where Vitest execution is unavailable.

---

## File Map

- Modify: `web_ui_vite/src/layouts/MainLayout.vue`
  - Reframe shell titles and panel chrome to match the new hierarchy.
- Modify: `web_ui_vite/src/components/SidebarHistory.vue`
  - Move filtering above management, compress low-frequency actions.
- Modify: `web_ui_vite/src/components/CanvasViewer.vue`
  - Simplify workspace toolbar and status strip hierarchy.
- Modify: `web_ui_vite/src/components/SidebarControls.vue`
  - Rebuild right rail into runtime -> models -> results -> actions -> danger order.
- Modify: `web_ui_vite/src/App.vue`
  - Pass any new labels/state needed for the reorganized sidebars.
- Modify: `web_ui_vite/tests/sidebar-controls.test.js`
  - Source-facing / component-level expectations for the right rail wording and sections.
- Create or Modify: `tests/test_ui_information_architecture.py`
  - Source-level regression checks for panel labels and ordering if needed.

## Chunk 1: Lock Layout Intent

### Task 1: Add failing checks for right-rail workflow wording

**Files:**
- Modify: `web_ui_vite/tests/sidebar-controls.test.js`
- Test: `web_ui_vite/tests/sidebar-controls.test.js`

- [ ] **Step 1: Write the failing test**

Add expectations for:
- `运行模式`
- `检测模型`
- `分类模型`
- `当前结果`
- `上传操作`
- `导出操作`

- [ ] **Step 2: Run test to verify it fails**

Run: `cd web_ui_vite && npm test -- --run tests/sidebar-controls.test.js`
Expected: FAIL because the new section labels do not exist yet.

- [ ] **Step 3: If Vitest is blocked by local Node runtime, add a Python source-level fallback test**

Create `tests/test_ui_information_architecture.py` that asserts the Vue source contains the required section titles.

- [ ] **Step 4: Run the fallback test to verify it fails**

Run: `python3 -m unittest tests/test_ui_information_architecture.py`
Expected: FAIL until the new labels are implemented.

## Chunk 2: Rebuild the Right Rail

### Task 2: Make the right rail reflect the actual workflow

**Files:**
- Modify: `web_ui_vite/src/components/SidebarControls.vue`
- Modify: `web_ui_vite/src/App.vue`
- Test: `web_ui_vite/tests/sidebar-controls.test.js`
- Test: `tests/test_ui_information_architecture.py`

- [ ] **Step 1: Implement the minimal right-rail restructure**

Change the right rail sections to:
- Runtime mode
- Active models
- Current result
- Current image re-detect
- Upload
- Export
- Danger zone

- [ ] **Step 2: Keep existing props and add only the minimal new display props**

Use current runtime metadata already available in `App.vue`:
- `twoStageEnabled`
- classification model name/path
- stage-1 count
- normal/abnormal counts

- [ ] **Step 3: Run the fallback/source tests**

Run: `python3 -m unittest tests/test_ui_information_architecture.py`
Expected: PASS

- [ ] **Step 4: Run any available frontend test command**

Run: `cd web_ui_vite && npm test -- --run tests/sidebar-controls.test.js`
Expected: PASS if environment allows; otherwise capture the Node/runtime failure explicitly.

## Chunk 3: Simplify the Left Rail

### Task 3: Make history browsing primary and management secondary

**Files:**
- Modify: `web_ui_vite/src/components/SidebarHistory.vue`
- Test: `tests/test_ui_information_architecture.py`

- [ ] **Step 1: Write or extend failing source assertions**

Assert that:
- filters appear before destructive/history management labels
- management actions are grouped under a lower-priority heading or compact block

- [ ] **Step 2: Run the source test to verify it fails**

Run: `python3 -m unittest tests/test_ui_information_architecture.py`
Expected: FAIL

- [ ] **Step 3: Implement the minimal left-rail restructure**

Reorder the top of the component to:
- title/summary
- filters
- compact management block
- history list

- [ ] **Step 4: Re-run source tests**

Run: `python3 -m unittest tests/test_ui_information_architecture.py`
Expected: PASS

## Chunk 4: Tighten the Center Workspace

### Task 4: Reduce toolbar noise and reinforce the active work area

**Files:**
- Modify: `web_ui_vite/src/components/CanvasViewer.vue`
- Test: `tests/test_ui_information_architecture.py`

- [ ] **Step 1: Add failing source assertions**

Assert that the center toolbar and status strip wording emphasize:
- image work
- selected box editing
- current result summary

- [ ] **Step 2: Run the source test to verify it fails**

Run: `python3 -m unittest tests/test_ui_information_architecture.py`
Expected: FAIL

- [ ] **Step 3: Implement the minimal center-panel cleanup**

Keep zoom/add-box actions, simplify labels, reduce visual competition from secondary actions.

- [ ] **Step 4: Run the source tests again**

Run: `python3 -m unittest tests/test_ui_information_architecture.py`
Expected: PASS

## Chunk 5: Polish Shell Chrome

### Task 5: Make the shell feel more futuristic without adding noise

**Files:**
- Modify: `web_ui_vite/src/layouts/MainLayout.vue`
- Test: `tests/test_ui_information_architecture.py`

- [ ] **Step 1: Add failing source assertions for panel titles**

Assert the shell titles reflect:
- records/history intent on the left
- task/action intent on the right

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests/test_ui_information_architecture.py`
Expected: FAIL

- [ ] **Step 3: Update shell titles and chrome**

Use tighter, more intentional visual framing while preserving the existing three-column structure.

- [ ] **Step 4: Re-run source tests**

Run: `python3 -m unittest tests/test_ui_information_architecture.py`
Expected: PASS

## Final Verification

- [ ] **Step 1: Run backend-safe verification**

Run: `python3 -m unittest tests/test_two_stage_classification.py tests/test_notebooks.py tests/test_ui_information_architecture.py`
Expected: PASS

- [ ] **Step 2: Run syntax/format sanity checks**

Run: `git diff --check`
Expected: no output

- [ ] **Step 3: Run available frontend verification**

Run: `cd web_ui_vite && npm run build`
Expected: PASS if local Node runtime supports it; otherwise capture the exact runtime blocker without claiming success.

- [ ] **Step 4: Commit**

```bash
git add web_ui_vite/src/layouts/MainLayout.vue \
  web_ui_vite/src/components/SidebarHistory.vue \
  web_ui_vite/src/components/CanvasViewer.vue \
  web_ui_vite/src/components/SidebarControls.vue \
  web_ui_vite/src/App.vue \
  web_ui_vite/tests/sidebar-controls.test.js \
  tests/test_ui_information_architecture.py \
  docs/superpowers/specs/2026-03-19-web-ui-information-architecture-design.md \
  docs/superpowers/plans/2026-03-19-web-ui-information-architecture.md
git commit -m "Reorganize web UI information architecture"
```
