import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import SidebarControls from '@/components/SidebarControls.vue'
import { useDetectionState } from '@/composables/useDetectionState'

function resetState() {
  const state = useDetectionState()
  state.pendingFiles.value = []
  state.processedFiles.value = []
  state.selectedFileItems.value.clear()
  state.availableModels.value = []
  state.currentModelKey.value = null
  state.modelClasses.value = {}
  return state
}

describe('SidebarControls', () => {
  it('acts as the main operations sidebar without rendering a duplicate file list', async () => {
    const state = resetState()
    state.modelClasses.value = { 0: 'normal', 1: 'abnormal' }
    state.currentModelKey.value = 'demo'
    state.availableModels.value = [
      { key: 'demo', name: 'Demo Model', description: 'single-class' }
    ]

    const wrapper = mount(SidebarControls, {
      props: {
        currentImagePath: 'example.jpg',
        currentDetections: [{ id: 1 }],
        detectionCount: 1,
        normalCount: 1,
        abnormalCount: 0,
        twoStageEnabled: true,
        avgConfidence: '0.95',
        statusValue: '检测完成',
        isBatchProcessing: false,
        isRedetecting: false,
        isModelSwitching: false
      }
    })

    expect(wrapper.text()).not.toContain('文件列表')
    expect(wrapper.text()).not.toContain('全选')
    expect(wrapper.text()).toContain('选择文件')
    expect(wrapper.text()).toContain('文件夹')
    expect(wrapper.text()).toContain('切换模型')
    expect(wrapper.text()).toContain('重新检测当前图片')
    expect(wrapper.text()).toContain('恢复默认阈值')
    expect(wrapper.text()).toContain('默认：confidence 0.80 / IoU 0.30')
    expect(wrapper.text()).toContain('清空所有文件')
    expect(wrapper.text()).toContain('导出当前结果')
    expect(wrapper.text()).toContain('检测状态')
    expect(wrapper.text()).toContain('检测数量')
    expect(wrapper.text()).toContain('平均置信度')
    expect(wrapper.text()).toContain('二阶段结果')
    expect(wrapper.text()).toContain('正常数量')
    expect(wrapper.text()).toContain('异常数量')
  })
})
