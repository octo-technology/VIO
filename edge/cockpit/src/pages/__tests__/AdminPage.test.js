import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import AdminPage from '../AdminPage.vue'

const vuetify = createVuetify({ components, directives })

describe('AdminPage', () => {
  it('renders the administration placeholder', () => {
    const wrapper = mount(AdminPage, {
      global: { plugins: [vuetify] },
    })
    expect(wrapper.text()).toContain('Administration')
  })

  it('mentions coming soon', () => {
    const wrapper = mount(AdminPage, {
      global: { plugins: [vuetify] },
    })
    expect(wrapper.text()).toContain('coming soon')
  })
})
