import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import CanvasViewer from '@/components/CanvasViewer.vue'
import { useDetectionState } from '@/composables/useDetectionState'

describe('CanvasViewer', () => {
  it('declares and emits the detection-hover event', async () => {
    const wrapper = mount(CanvasViewer, {
      props: {
        detections: [{ id: 7, bbox: [10, 10, 20, 20], confidence: 0.9, class_id: 0 }]
      }
    })

    expect(wrapper.vm.$.emitsOptions).toHaveProperty('detection-hover')
  })

  it('keeps the settings panel scrollable when content grows taller', async () => {
    const wrapper = mount(CanvasViewer)

    wrapper.vm.showBoxSettings()
    await wrapper.vm.$nextTick()

    const settingsPanel = wrapper.find('[data-testid="settings-panel"]')

    expect(settingsPanel.classes()).toContain('overflow-y-auto')
    expect(settingsPanel.classes()).toContain('max-h-[calc(100vh-7rem)]')
  })

  it('keeps the settings panel focused on box styles instead of task actions', async () => {
    const wrapper = mount(CanvasViewer)

    wrapper.vm.showBoxSettings()
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('检测框样式')
    expect(wrapper.text()).not.toContain('重新检测当前图片')
    expect(wrapper.text()).not.toContain('选择模型')
    expect(wrapper.text()).not.toContain('清空所有文件')
  })

  it('lets the user change the class label of the selected detection', async () => {
    const state = useDetectionState()
    state.modelClasses.value = { 0: 'normal', 1: 'abnormal' }

    const wrapper = mount(CanvasViewer, {
      props: {
        detections: [
          { id: 1, bbox: [10, 10, 40, 40], confidence: 0.92, class_id: 0, class_name: 'normal' }
        ],
        selectedDetectionBoxes: new Set([1])
      }
    })

    const select = wrapper.find('[data-testid="detection-class-select"]')
    expect(select.exists()).toBe(true)

    await select.setValue('1')

    expect(wrapper.emitted('update-detection-class')).toEqual([[
      {
        detectionId: 1,
        classId: 1,
        className: 'abnormal'
      }
    ]])
  })

  it('lets the user add a new detection box for manual correction', async () => {
    const wrapper = mount(CanvasViewer, {
      props: {
        imageBase64: 'ZmFrZQ=='
      }
    })

    wrapper.vm.hasImage = true
    wrapper.vm.canvasWidth = 400
    wrapper.vm.canvasHeight = 200
    await wrapper.vm.$nextTick()

    const addButton = wrapper.find('[data-testid="add-detection-button"]')
    expect(addButton.exists()).toBe(true)

    await addButton.trigger('click')

    expect(wrapper.emitted('add-detection')).toEqual([[
      {
        bbox: [150, 50, 250, 150]
      }
    ]])
  })

  it('lets the user resize the selected detection from the correction panel', async () => {
    const state = useDetectionState()
    state.modelClasses.value = { 0: 'normal', 1: 'abnormal' }

    const wrapper = mount(CanvasViewer, {
      props: {
        detections: [
          { id: 1, bbox: [10, 10, 50, 60], confidence: 0.92, class_id: 0, class_name: 'normal' }
        ],
        selectedDetectionBoxes: new Set([1])
      }
    })

    const widthInput = wrapper.find('[data-testid="detection-width-input"]')
    expect(widthInput.exists()).toBe(true)

    await widthInput.setValue('80')

    expect(wrapper.emitted('update-detection-bbox')).toEqual([[
      {
        detectionId: 1,
        bbox: [10, 10, 90, 60]
      }
    ]])
  })
})
