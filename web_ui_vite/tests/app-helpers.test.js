import { describe, expect, it, vi } from 'vitest'
import {
  buildExportAnnotationPayload,
  deleteSelectedDetectionsOnServer,
  prepareComparisonItems
} from '@/utils/appHelpers'

describe('appHelpers', () => {
  it('reloads missing comparison images before opening the comparison view', async () => {
    const reloadImage = vi.fn(async (imagePath) => ({
      success: true,
      image_base64: `reloaded:${imagePath}`
    }))

    const items = [
      { imageName: 'ready.jpg', imageBase64: 'cached', path: '/tmp/ready.jpg' },
      { imageName: 'missing.jpg', imageBase64: null, path: '/tmp/missing.jpg' }
    ]

    const result = await prepareComparisonItems(items, reloadImage)

    expect(reloadImage).toHaveBeenCalledTimes(1)
    expect(result[0].imageBase64).toBe('cached')
    expect(result[1].imageBase64).toBe('reloaded:/tmp/missing.jpg')
  })

  it('deletes selected detections through the backend and reindexes the survivors', async () => {
    const deleteDetection = vi.fn(async () => ({ success: true }))
    const detections = [
      { id: 1, bbox: [0, 0, 10, 10], confidence: 0.9 },
      { id: 2, bbox: [10, 10, 20, 20], confidence: 0.8 },
      { id: 3, bbox: [20, 20, 30, 30], confidence: 0.7 }
    ]

    const result = await deleteSelectedDetectionsOnServer({
      imagePath: '/tmp/example.jpg',
      detections,
      selectedIds: new Set([2]),
      deleteDetection
    })

    expect(deleteDetection).toHaveBeenCalledWith('/tmp/example.jpg', 2)
    expect(result.deletedCount).toBe(1)
    expect(result.detections.map(d => d.id)).toEqual([1, 2])
    expect(result.detections.map(d => d.confidence)).toEqual([0.9, 0.7])
  })

  it('falls back to local deletion when no exported json exists yet', async () => {
    const deleteDetection = vi.fn(async () => {
      throw new Error('JSON 文件不存在')
    })

    const result = await deleteSelectedDetectionsOnServer({
      imagePath: '/tmp/example.jpg',
      detections: [
        { id: 1, bbox: [0, 0, 10, 10], confidence: 0.9 },
        { id: 2, bbox: [10, 10, 20, 20], confidence: 0.8 }
      ],
      selectedIds: new Set([1]),
      deleteDetection
    })

    expect(result.deletedCount).toBe(1)
    expect(result.usedLocalFallback).toBe(true)
    expect(result.detections.map(d => d.id)).toEqual([1])
  })

  it('builds an export payload that keeps corrected instance annotations for second-stage training', () => {
    const payload = buildExportAnnotationPayload({
      imagePath: '20260313_demo.jpg',
      imageName: 'DJI_001.jpg',
      originalPath: 'folderA/DJI_001.jpg',
      detections: [
        {
          id: 3,
          bbox: [10, 20, 110, 220],
          confidence: 0.91,
          class_id: 1,
          class_name: 'abnormal'
        }
      ],
      modelInfo: {
        key: 'demo-model',
        name: 'YOLO11X | 2类 | exp008 | base005'
      }
    })

    expect(payload.image_path).toBe('20260313_demo.jpg')
    expect(payload.original_path).toBe('folderA/DJI_001.jpg')
    expect(payload.instances).toEqual([
      {
        id: 3,
        image_path: '20260313_demo.jpg',
        original_path: 'folderA/DJI_001.jpg',
        class_id: 1,
        class_name: 'abnormal',
        bbox: [10, 20, 110, 220],
        confidence: 0.91
      }
    ])
  })
})
