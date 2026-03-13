import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import CanvasViewer from '@/components/CanvasViewer.vue'

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
})
