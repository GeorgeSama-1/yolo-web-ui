export async function prepareComparisonItems(items, reloadImage) {
  const preparedItems = []

  for (const item of items) {
    let imageBase64 = item.imageBase64 || item.thumbnailBase64 || null

    if (!imageBase64 && item.path) {
      try {
        const result = await reloadImage(item.path)
        if (result?.success && result.image_base64) {
          imageBase64 = result.image_base64
        }
      } catch (error) {
        imageBase64 = item.thumbnailBase64 || null
      }
    }

    preparedItems.push({
      ...item,
      imageBase64
    })
  }

  return preparedItems
}

export function buildExportAnnotationPayload({
  imagePath,
  imageName,
  originalPath,
  detections,
  modelInfo
}) {
  const finalOriginalPath = originalPath || imageName || null
  const normalizedDetections = (detections || []).map(detection => ({
    ...detection,
    class_id: detection.class_id ?? 0,
    class_name: detection.class_name ?? `class_${detection.class_id ?? 0}`
  }))

  return {
    image_path: imagePath,
    image_name: imageName || null,
    original_path: finalOriginalPath,
    detections: normalizedDetections,
    instances: normalizedDetections.map(detection => ({
      id: detection.id,
      image_path: imagePath,
      original_path: finalOriginalPath,
      class_id: detection.class_id,
      class_name: detection.class_name,
      bbox: detection.bbox,
      confidence: detection.confidence
    })),
    model_info: modelInfo || null
  }
}

export async function deleteSelectedDetectionsOnServer({
  imagePath,
  detections,
  selectedIds,
  deleteDetection
}) {
  const ids = Array.from(selectedIds)
  let usedLocalFallback = false

  for (const detectionId of ids) {
    try {
      const result = await deleteDetection(imagePath, detectionId)
      if (!result?.success) {
        throw new Error(result?.error || `Failed to delete detection ${detectionId}`)
      }
    } catch (error) {
      if (!String(error?.message || '').includes('JSON 文件不存在')) {
        throw error
      }
      usedLocalFallback = true
    }
  }

  const remainingDetections = detections
    .filter(detection => !selectedIds.has(detection.id))
    .map((detection, index) => ({
      ...detection,
      id: index + 1
    }))

  return {
    deletedCount: ids.length,
    detections: remainingDetections,
    usedLocalFallback
  }
}

export function buildComparisonHtml(selectedItems) {
  return `
    <!DOCTYPE html>
    <html>
    <head>
      <title>模型对比</title>
      <style>
        * { box-sizing: border-box; }
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #1a1a2e; min-height: 100vh; }
        h1 { color: #fff; text-align: center; padding: 10px 0 20px; margin: 0; }
        .comparison-grid {
          display: grid;
          grid-template-columns: repeat(${Math.min(selectedItems.length, 2)}, 1fr);
          gap: 20px;
          max-width: 1400px;
          margin: 0 auto;
        }
        .comparison-item {
          background: #16213e;
          border-radius: 12px;
          overflow: hidden;
          box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }
        .item-header {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          padding: 15px 20px;
          color: white;
        }
        .model-name { font-size: 18px; font-weight: bold; margin-bottom: 5px; }
        .image-name { font-size: 13px; opacity: 0.9; }
        .item-stats {
          display: flex;
          justify-content: space-around;
          padding: 15px;
          background: #0f3460;
          color: #fff;
        }
        .stat { text-align: center; }
        .stat-value { font-size: 28px; font-weight: bold; color: #e94560; }
        .stat-label { font-size: 12px; color: #aaa; margin-top: 3px; }
        .item-image {
          width: 100%;
          aspect-ratio: 4/3;
          object-fit: contain;
          background: #000;
          display: block;
        }
        .item-detections {
          padding: 15px;
          max-height: 150px;
          overflow-y: auto;
          background: #1a1a2e;
        }
        .detection-item {
          display: flex;
          justify-content: space-between;
          padding: 8px 12px;
          margin: 5px 0;
          background: #16213e;
          border-radius: 6px;
          color: #fff;
          font-size: 13px;
        }
        .detection-conf { color: #4ade80; font-weight: 600; }
      </style>
    </head>
    <body>
      <h1>📊 模型检测结果对比 (${selectedItems.length} 张图片)</h1>
      <div class="comparison-grid">
        ${selectedItems.map(item => {
          const avgConf = item.detections && item.detections.length > 0
            ? (item.detections.reduce((sum, d) => sum + d.confidence, 0) / item.detections.length).toFixed(3)
            : '-'
          const imageBase64 = item.imageBase64 || ''
          return `
            <div class="comparison-item">
              <div class="item-header">
                <div class="model-name">${item.modelInfo ? item.modelInfo.name : '未知模型'}</div>
                <div class="image-name">📷 ${item.imageName}</div>
              </div>
              <div class="item-stats">
                <div class="stat">
                  <div class="stat-value">${item.count}</div>
                  <div class="stat-label">检测数量</div>
                </div>
                <div class="stat">
                  <div class="stat-value">${avgConf}</div>
                  <div class="stat-label">平均置信度</div>
                </div>
                <div class="stat">
                  <div class="stat-value">${item.detections ? item.detections.length : 0}</div>
                  <div class="stat-label">检测框数</div>
                </div>
              </div>
              <img class="item-image" src="data:image/jpeg;base64,${imageBase64}" alt="${item.imageName}">
              ${item.detections && item.detections.length > 0 ? `
                <div class="item-detections">
                  ${item.detections.slice(0, 10).map((d, i) => `
                    <div class="detection-item">
                      <span>检测 #${i + 1}</span>
                      <span class="detection-conf">${(d.confidence * 100).toFixed(1)}%</span>
                    </div>
                  `).join('')}
                  ${item.detections.length > 10 ? `<div class="detection-item"><span>... 还有 ${item.detections.length - 10} 个检测框</span></div>` : ''}
                </div>
              ` : ''}
            </div>
          `
        }).join('')}
      </div>
    </body>
    </html>
  `
}
