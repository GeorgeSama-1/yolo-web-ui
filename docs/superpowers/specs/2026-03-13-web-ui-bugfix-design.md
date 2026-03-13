# Web UI Bugfix Design

## Scope

Fix the confirmed frontend defects in the Vite UI:

1. The file list "clear" action throws at runtime because the handler is missing.
2. Detection deletion only mutates client state and does not persist to the backend.
3. Model comparison opens with broken images when full image data is not cached.
4. History/file clearing behavior is inconsistent between frontend state and backend storage.
5. `CanvasViewer` emits an undeclared hover event, producing Vue warnings.

## Approach

Keep the current component structure and repair the broken behavior with minimal surface-area changes.

- Add targeted API helpers for backend-backed clear/delete flows.
- Move comparison image preparation into `App.vue` so the parent can reload missing image data before opening the comparison window.
- Make the right sidebar clear action clear both pending/processed file state and selections without throwing.
- Keep history clearing semantics explicit:
  - "清空所有历史" clears in-memory history only.
  - "清空所有文件" clears backend uploads/outputs and also clears in-memory state.
- Add component-level regression tests around the broken click handlers and emitted events, plus unit tests around the helper functions that now own the risky logic.

## Validation

- Run focused tests for the bugfix cases.
- Run a production build once dependencies are available.
