# Current Image Redetect Design

## Goal

Allow users to adjust confidence and IoU only for the currently viewed image, trigger an immediate re-detection from the existing settings panel, and automatically suppress overlapping `normal` / `abnormal` results with `abnormal` priority.

## Current State

- The Vite frontend has a settings panel but no confidence or IoU controls.
- The main backend entrypoint `app.py` runs detection with fixed thresholds.
- The current UI cannot refresh the selected image in place with different thresholds.
- Overlapping `normal` and `abnormal` boxes remain together, which hurts interaction.

## Design

### Frontend

- Add a `当前图片重检` section to the existing `CanvasViewer` settings panel.
- Controls:
  - confidence threshold slider/input
  - IoU threshold slider/input
  - `重新检测当前图片` button
- These controls affect only the current re-detection request and do not modify global defaults.
- The button is disabled when there is no current image.
- The panel emits a `redetect-current` event with the thresholds.

### Backend

- Add a new `/api/redetect` endpoint in `app.py`.
- Request payload:
  - `image_path`
  - `confidence_threshold`
  - `iou_threshold`
- The backend re-runs inference against the already stored upload image and returns fresh detections.
- Refactor overlap suppression into a pure helper module so it can be unit-tested without model dependencies.

### Overlap Rule

- Apply high-overlap suppression after detection extraction.
- When overlapping boxes are `normal` and `abnormal`, prefer `abnormal`.
- Use a small confidence margin so a very weak `abnormal` box does not override a much stronger `normal` box.
- For other classes, keep the standard confidence ordering.

### UI Update

- `App.vue` handles the new event, calls the backend, and updates:
  - current detections
  - current history item
  - current stats
  - matching processed file result if present
- Re-detection updates the current item in place and does not create a new history entry.

## Validation

- Frontend unit test for the settings panel re-detect event.
- Python unit test for abnormal-priority suppression.
- Existing frontend tests remain green.
- Production build remains green.
