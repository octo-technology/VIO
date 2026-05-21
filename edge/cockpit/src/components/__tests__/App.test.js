import { describe, it, expect, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import { createPinia } from 'pinia'
import App from '../../App.vue'

vi.mock('vue-router', () => ({
  useRoute: vi.fn(() => ({ path: '/operator' })),
  useRouter: vi.fn(() => ({})),
  RouterView: { template: '<div />' },
  RouterLink: { template: '<a><slot /></a>' },
}))

vi.mock('../../features/station-config/api/discoveryRepository', () => ({
  getCamerasAvailable: vi.fn().mockResolvedValue({ cameras: {} }),
  getModelsAvailable: vi.fn().mockResolvedValue({ models: {} }),
}))

const vuetify = createVuetify({ components, directives })
const pinia = createPinia()

function mountApp() {
  return mount(App, {
    global: {
      plugins: [vuetify, pinia],
      stubs: {
        'v-app-bar': { template: '<div><slot /><slot name="append" /></div>' },
        'v-navigation-drawer': {
          template: '<div data-testid="drawer"><slot /><slot name="append" /></div>',
          props: ['rail'],
        },
        RouterView: { template: '<div />' },
      },
    },
  })
}

describe('App sidebar', () => {
  it('shows nav item titles when expanded', async () => {
    const wrapper = mountApp()
    await flushPromises()
    expect(wrapper.text()).toContain('Live Inspection')
    expect(wrapper.text()).toContain('Configuration')
    expect(wrapper.text()).toContain('Administration')
  })

  it('renders a collapse toggle button', async () => {
    const wrapper = mountApp()
    await flushPromises()
    expect(wrapper.text()).toContain('Collapse')
  })

  it('toggles rail mode when collapse button is clicked', async () => {
    const wrapper = mountApp()
    await flushPromises()

    // Expanded: "Collapse" label visible
    expect(wrapper.text()).toContain('Collapse')

    const toggleBtn = wrapper.findAll('.v-list-item').find((el) => el.text().includes('Collapse'))
    await toggleBtn.trigger('click')
    await flushPromises()

    // Collapsed: title becomes empty string, "Collapse" label gone
    expect(wrapper.text()).not.toContain('Collapse')
  })

  it('changes chevron icon direction when collapsed', async () => {
    const wrapper = mountApp()
    await flushPromises()

    // Expanded: chevron-left
    expect(wrapper.html()).toContain('mdi-chevron-left')
    expect(wrapper.html()).not.toContain('mdi-chevron-right')

    const toggleBtn = wrapper.findAll('.v-list-item').find((el) => el.text().includes('Collapse'))
    await toggleBtn.trigger('click')
    await flushPromises()

    // Collapsed: chevron-right
    expect(wrapper.html()).toContain('mdi-chevron-right')
  })
})
