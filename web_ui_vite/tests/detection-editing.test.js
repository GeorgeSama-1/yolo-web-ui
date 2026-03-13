import { describe, expect, it } from 'vitest'
import {
  clampBBoxToCanvas,
  createCenteredBBox,
  moveBBox,
  resizeBBoxFromHandle
} from '@/utils/detectionEditing'

describe('detectionEditing', () => {
  it('creates a centered bbox inside the canvas bounds', () => {
    expect(createCenteredBBox(400, 200)).toEqual([150, 50, 250, 150])
  })

  it('moves a bbox while keeping it inside the canvas bounds', () => {
    expect(moveBBox([10, 10, 60, 60], 80, 50, 120, 100)).toEqual([70, 50, 120, 100])
  })

  it('resizes a bbox from the south-east handle', () => {
    expect(
      resizeBBoxFromHandle({
        bbox: [10, 10, 50, 60],
        handle: 'se',
        deltaX: 30,
        deltaY: 20,
        canvasWidth: 200,
        canvasHeight: 200
      })
    ).toEqual([10, 10, 80, 80])
  })

  it('clamps tiny or overflowing bboxes back into a valid canvas area', () => {
    expect(clampBBoxToCanvas([-10, -10, 5, 5], 100, 100)).toEqual([0, 0, 20, 20])
  })
})
