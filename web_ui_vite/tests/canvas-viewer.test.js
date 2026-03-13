import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import CanvasViewer from '@/components/CanvasViewer.vue'
import { useDetectionState } from '@/composables/useDetectionState'

function setupCanvasGeometry(wrapper, { width = 100, height = 100 } = {}) {
  const canvas = wrapper.find('canvas')
  canvas.element.getBoundingClientRect = () => ({
    left: 0,
    top: 0,
    width,
    height,
    right: width,
    bottom: height
  })
  return canvas
}

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
    expect(wrapper.find('[data-testid="detection-width-input"]').exists()).toBe(false)
    expect(wrapper.find('[data-testid="detection-height-input"]').exists()).toBe(false)

    await select.setValue('1')

    expect(wrapper.emitted('update-detection-class')).toEqual([[
      {
        detectionId: 1,
        classId: 1,
        className: 'abnormal'
      }
    ]])
  })

  it('uses an inset highlight overlay for the selected detection instead of an outer border', async () => {
    const wrapper = mount(CanvasViewer, {
      props: {
        detections: [
          { id: 1, bbox: [10, 10, 40, 40], confidence: 0.92, class_id: 0, class_name: 'normal' }
        ],
        selectedDetectionBoxes: new Set([1])
      }
    })

    const overlay = wrapper.find('.shadow-\\[inset_0_0_0_2px_\\#34d399\\]')
    expect(overlay.exists()).toBe(true)
    expect(overlay.classes()).not.toContain('border-2')
  })

  it('enters draw mode so the user can drag out a custom detection box', async () => {
    const wrapper = mount(CanvasViewer)

    wrapper.vm.hasImage = true
    await wrapper.vm.$nextTick()

    const addButton = wrapper.find('[data-testid="add-detection-button"]')
    expect(addButton.text()).toContain('补加框')

    await addButton.trigger('click')

    expect(addButton.text()).toContain('拖拽补框中')
  })

  it('starts dragging an original detection box on first mouse down like a label editor', async () => {
    const wrapper = mount(CanvasViewer, {
      props: {
        detections: [
          { id: 1, bbox: [10, 10, 50, 50], confidence: 0.92, class_id: 0, class_name: 'normal' }
        ]
      }
    })

    wrapper.vm.hasImage = true
    wrapper.vm.canvasWidth = 100
    wrapper.vm.canvasHeight = 100
    await wrapper.vm.$nextTick()

    const canvas = setupCanvasGeometry(wrapper)

    await canvas.trigger('mousedown', { clientX: 20, clientY: 20 })
    await canvas.trigger('mousemove', { clientX: 30, clientY: 30 })

    expect(wrapper.emitted('detection-click')).toEqual([[1]])
    expect(wrapper.emitted('update-detection-bbox')).toEqual([[
      {
        detectionId: 1,
        bbox: [20, 20, 60, 60]
      }
    ]])
  })

  it('does not emit box updates when the pointer starts on empty canvas space', async () => {
    const wrapper = mount(CanvasViewer, {
      props: {
        detections: [
          { id: 1, bbox: [10, 10, 50, 50], confidence: 0.92, class_id: 0, class_name: 'normal' }
        ]
      }
    })

    wrapper.vm.hasImage = true
    wrapper.vm.canvasWidth = 100
    wrapper.vm.canvasHeight = 100
    await wrapper.vm.$nextTick()

    const canvas = setupCanvasGeometry(wrapper)

    await canvas.trigger('mousedown', { clientX: 80, clientY: 80 })
    await canvas.trigger('mousemove', { clientX: 90, clientY: 90 })
    await canvas.trigger('mouseup', { clientX: 90, clientY: 90 })

    expect(wrapper.emitted('update-detection-bbox')).toBeUndefined()
  })

  it('renders canvas overlay handles for resizing the selected detection', async () => {
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

    await wrapper.vm.$nextTick()

    const handles = wrapper.findAll('button.cursor-nwse-resize, button.cursor-nesw-resize')
    expect(handles.length).toBe(4)
  })
})
