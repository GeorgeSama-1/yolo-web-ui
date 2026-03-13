const MIN_BOX_SIZE = 20

export function clampBBoxToCanvas(bbox, canvasWidth, canvasHeight, minSize = MIN_BOX_SIZE) {
  let [x1, y1, x2, y2] = bbox.map(value => Math.round(value))

  x1 = Math.max(0, Math.min(x1, canvasWidth))
  y1 = Math.max(0, Math.min(y1, canvasHeight))
  x2 = Math.max(0, Math.min(x2, canvasWidth))
  y2 = Math.max(0, Math.min(y2, canvasHeight))

  if (x2 - x1 < minSize) {
    x2 = Math.min(x1 + minSize, canvasWidth)
    x1 = Math.max(x2 - minSize, 0)
  }

  if (y2 - y1 < minSize) {
    y2 = Math.min(y1 + minSize, canvasHeight)
    y1 = Math.max(y2 - minSize, 0)
  }

  return [x1, y1, x2, y2]
}

export function createCenteredBBox(canvasWidth, canvasHeight) {
  const boxWidth = Math.max(Math.round(canvasWidth * 0.25), 80)
  const boxHeight = Math.max(Math.round(canvasHeight * 0.5), 80)
  const x1 = Math.max(Math.round((canvasWidth - boxWidth) / 2), 0)
  const y1 = Math.max(Math.round((canvasHeight - boxHeight) / 2), 0)
  return clampBBoxToCanvas([x1, y1, x1 + boxWidth, y1 + boxHeight], canvasWidth, canvasHeight)
}

export function moveBBox(bbox, deltaX, deltaY, canvasWidth, canvasHeight) {
  const [x1, y1, x2, y2] = bbox
  const width = x2 - x1
  const height = y2 - y1
  const nextX1 = Math.min(Math.max(Math.round(x1 + deltaX), 0), Math.max(canvasWidth - width, 0))
  const nextY1 = Math.min(Math.max(Math.round(y1 + deltaY), 0), Math.max(canvasHeight - height, 0))
  return [nextX1, nextY1, nextX1 + width, nextY1 + height]
}

export function resizeBBoxFromHandle({
  bbox,
  handle,
  deltaX,
  deltaY,
  canvasWidth,
  canvasHeight,
  minSize = MIN_BOX_SIZE
}) {
  let [x1, y1, x2, y2] = bbox

  if (handle.includes('n')) {
    y1 += deltaY
  }
  if (handle.includes('s')) {
    y2 += deltaY
  }
  if (handle.includes('w')) {
    x1 += deltaX
  }
  if (handle.includes('e')) {
    x2 += deltaX
  }

  if (x2 - x1 < minSize) {
    if (handle.includes('w')) {
      x1 = x2 - minSize
    } else {
      x2 = x1 + minSize
    }
  }

  if (y2 - y1 < minSize) {
    if (handle.includes('n')) {
      y1 = y2 - minSize
    } else {
      y2 = y1 + minSize
    }
  }

  return clampBBoxToCanvas([x1, y1, x2, y2], canvasWidth, canvasHeight, minSize)
}
