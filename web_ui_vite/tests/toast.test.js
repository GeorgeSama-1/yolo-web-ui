import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import Toast from '@/components/shared/Toast.vue'

describe('Toast', () => {
  it('renders as a floating notification near the upper center of the screen', async () => {
    const wrapper = mount(Toast, {
      attachTo: document.body,
      props: {
        show: true,
        type: 'success',
        title: '模型切换成功'
      }
    })

    await wrapper.vm.$nextTick()

    const toast = document.body.querySelector('[data-testid="toast"]')

    expect(toast).not.toBeNull()
    expect(toast.className).toContain('fixed')
    expect(toast.className).toContain('top-16')
    expect(toast.className).toContain('left-1/2')
    expect(toast.className).toContain('-translate-x-1/2')

    wrapper.unmount()
  })
})
