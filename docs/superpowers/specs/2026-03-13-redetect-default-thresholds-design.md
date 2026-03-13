# Redetect Default Threshold Reset Design

## Goal

Add a small reset action in the existing current-image redetect settings so users can restore the default confidence and IoU thresholds without triggering a re-detection automatically.

## Design

- Add a `恢复默认阈值` button in the `重新检测当前图片` section of the settings panel.
- Clicking the button resets:
  - confidence threshold to `0.80`
  - IoU threshold to `0.30`
- The reset only updates the local controls.
- It does not call the backend and does not emit a re-detect event.

## Validation

- Add a Vitest case proving the controls reset to the defaults.
- Existing viewer event tests remain green.
