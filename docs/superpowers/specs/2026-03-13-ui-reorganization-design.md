# UI Reorganization Design

## Goal

Reduce clutter by reorganizing the interface around the user task flow without removing existing capabilities.

## Design

### Information Architecture

- Left panel: history and filtering only
- Center panel: image viewing and direct annotation interaction
- Right panel: current-task operations only

### Right Panel Responsibilities

- Current model and model switching
- Current image summary and live stats
- Current-image re-detection parameters and actions
- Upload actions
- Export actions
- Class summary
- Destructive data-management action grouped at the bottom

### Settings Popup Responsibilities

- Only viewer-style settings remain:
  - box line width
  - font size
- Remove model switching, re-detect controls, and clear-all-files from the popup

### Interaction Principles

- High-frequency actions stay visible in the right sidebar
- Low-frequency appearance settings stay in the popup
- Dangerous actions remain separated from upload/export
- No duplicate lists across left and right panels

## Validation

- Add focused sidebar component tests for the new action flow
- Keep existing viewer interaction tests green
- Run full frontend test suite and production build
