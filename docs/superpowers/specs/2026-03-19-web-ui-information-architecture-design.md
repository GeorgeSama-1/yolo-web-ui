# Web UI Information Architecture Design

## Goal

Reorganize the Web UI so the page reads as a clear workflow tool instead of a collection of stacked features. The primary user flow is:

1. Upload an image
2. Inspect the current result
3. Correct boxes or labels
4. Export or mark the result

The redesign should preserve existing capabilities, make the current operating mode obvious, and strengthen the overall sci-fi / industrial visual language without hiding core actions.

## Problems To Solve

### 1. Information hierarchy is inverted

Low-frequency list management actions dominate the left rail. The right rail mixes model state, upload, redetect, export, and destructive actions without a clear order. The center area contains the main work but is visually surrounded by competing controls.

### 2. Workflow status is unclear

Users cannot quickly tell whether the page is currently operating in:

- stage-1 detection only
- two-stage detection + classification

The system also does not make the active detection model and classification model feel like part of one coherent runtime state.

### 3. Visual emphasis does not match user intent

The page already uses a “tech” style, but the decorative treatment currently competes with the workflow rather than reinforcing it. The UI should feel more deliberate and futuristic while remaining readable and task-first.

## Design Principles

### A. One panel, one job

- Left rail: records and filters
- Center: current image and annotation work
- Right rail: runtime state and actions

### B. Current-task-first

Anything related to the currently loaded image should live in or near the center/right flow. History management should not dominate the first screenful.

### C. Runtime state must be explicit

The user should always be able to answer:

- which detection model is active
- whether classification is enabled
- which classification model is active
- what the current image result summary is

### D. Futuristic, but legible

The redesign should keep the science/industrial tone, but reduce noisy chrome and improve spacing, grouping, and contrast. Technology styling should frame the work, not overwhelm it.

## Layout Design

### Left Rail: Records

The left rail remains the history surface, but its internal hierarchy changes.

#### Top section

The very top should focus on filtering and orientation:

- history title
- model filter
- count filter
- result count summary

#### Secondary actions

List-management actions become a smaller secondary control row or compact management block:

- select all
- clear selection
- delete selected
- clear marks
- clear history

These actions remain available, but no longer dominate the first visible section.

#### Main content

The history list remains the core of the left panel. Folder grouping stays, because it supports batch browsing and model comparison.

### Center Workspace: Inspect and Correct

The center panel becomes the single, obvious workspace.

#### Toolbar

The top toolbar should contain only direct image-work actions:

- zoom in / out
- fit to window
- actual size
- add box

The current image name remains visible, but with stronger emphasis and better truncation.

#### Result strip

A compact strip beneath the toolbar summarizes the current image:

- stage-1 count
- selected count
- class summary chips

If two-stage mode is enabled, the summary should feel additive rather than replacing the core inspection flow.

#### Annotation strip

The selected-box editing strip stays near the canvas because it is part of the active correction task. It should remain focused on:

- selected box identity
- class editing
- short editing hint

#### Bottom actions

Pass / fail marking stays at the bottom for now, but should have reduced visual weight relative to the canvas itself.

### Right Rail: Runtime and Actions

The right panel becomes a single ordered task panel.

#### Section order

1. Runtime mode
2. Active models
3. Current result summary
4. Current image re-detect controls
5. Upload actions
6. Export actions
7. Danger zone

This order mirrors the mental model:

- what mode am I in?
- what models are driving it?
- what happened on this image?
- what can I do next?

#### Runtime mode section

This section must explicitly show:

- stage-1 only, or
- stage-1 + stage-2

#### Active models section

This section should separate:

- detection model
- classification model

If no classification model is configured, the UI must say so plainly rather than silently collapsing into stage-1 behavior.

#### Current result summary

This section should distinguish:

- stage-1 total count
- stage-2 normal count
- stage-2 abnormal count

If two-stage mode is not active, only stage-1 summary is emphasized.

## Visual Direction

### Tone

Keep the cyber-industrial style, but simplify the hierarchy:

- darker neutral base
- cyan as primary system accent
- amber for temporary actions / retest
- emerald for success/export
- rose/red for anomaly and danger

### Surface treatment

- stronger section separation through border glow and subtle elevation
- less gratuitous chrome in titles and headers
- more consistent card spacing and padding
- clearer headline/subheadline patterns

### Typography

- uppercase micro-labels for system metadata
- short, direct section titles in Chinese
- dense but readable operational copy

## Data and Behavior

### Backend expectations

No major API redesign is needed for this round. The frontend will consume the runtime and classification metadata already being added in parallel:

- `two_stage_enabled`
- `classification_model`
- `normal_count`
- `abnormal_count`
- `stage1_total_count`

### Frontend responsibilities

- reorder and regroup controls
- rename labels to reflect actual workflow
- keep current interactions intact
- visually surface runtime state instead of hiding it

## Testing Strategy

Because local Node tooling is currently constrained, the safest automated checks for this round are:

- targeted Python/unit checks for backend runtime metadata where needed
- source-level assertions in existing notebook/UI tests for key wording and structure
- `git diff --check`
- backend syntax compilation

Frontend component tests should still be updated where possible, but we should not claim Vitest execution unless the local Node runtime supports the dependency stack.

## Non-Goals

This redesign does not:

- add model upload management
- introduce a classification model selector yet
- change export formats
- redesign annotation mechanics
- rewrite the entire visual system

The focus is information architecture, entry placement, and clearer runtime expression.
