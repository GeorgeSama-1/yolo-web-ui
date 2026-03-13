# Dynamic Model Classes Design

## Goal

Make the web UI display detection class names from the currently loaded model instead of assuming fixed labels such as `insulator`, `normal`, or `abnormal`.

## Current State

- The backend already exposes the current model's classes through `/api/classes`.
- The frontend already stores that response in `modelClasses` and uses it in several places.
- The remaining mismatch is that some UI text is still hardcoded for the old binary-label assumption, especially the settings legend.
- A few backend fallbacks still default to `insulator`, which is fine for single-class models but not ideal as a generic fallback.

## Design

### Data Contract

Keep the current `/api/classes` response shape:

```json
{
  "success": true,
  "classes": {
    "0": "insulator"
  }
}
```

or for multi-class models:

```json
{
  "success": true,
  "classes": {
    "0": "normal",
    "1": "abnormal"
  }
}
```

No new API is required for this feature.

### Frontend Behavior

- `App.vue` continues loading classes on startup and after model switches.
- `useDetectionState` remains the single source of truth for class names and class colors.
- `CanvasViewer.vue` replaces the hardcoded settings legend with a dynamic list derived from `modelClasses`.
- Canvas labels and class breakdown keep using `getClassName(classId)`, which already follows the current model.
- `SidebarControls.vue` continues rendering the class list dynamically.
- `FileItem.vue` keeps showing `class_counts` by the class names returned from the backend.

### Fallback Strategy

- If a model does not expose names, backend fallback stays single-class by default.
- Frontend fallback remains `class_<id>` when a detection references a class id that is missing from `modelClasses`.
- Color assignment stays automatic on the frontend and is not tied to any specific label text.

## Scope

In scope:

- Dynamic class legend in the viewer settings panel
- Removal of hardcoded class-name assumptions in the Vite UI
- Small backend cleanup for generic label fallback where appropriate
- Regression tests for single-class and multi-class display

Out of scope:

- Manual class editing in the UI
- Persisting custom display names
- Changing the `/api/classes` response format
