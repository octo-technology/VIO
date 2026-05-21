import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import { createPinia, setActivePinia } from 'pinia'
import StatusBar from '../StatusBar.vue'
import { useHealthStore } from '../../features/system-health/stores/healthStore'

vi.mock('../../features/station-config/api/discoveryRepository', () => ({
  getCamerasAvailable: vi.fn(),
  getModelsAvailable: vi.fn(),
}))

import * as discoveryRepository from '../../features/station-config/api/discoveryRepository'

const vuetify = createVuetify({ components, directives })

let pinia

function mountBar() {
  return mount(StatusBar, {
    global: {
      plugins: [vuetify, pinia],
      stubs: {
        'v-app-bar': { template: '<div><slot /><slot name="append" /></div>' },
        'v-dialog': { template: '<div v-if="modelValue"><slot /></div>', props: ['modelValue'] },
      },
    },
  })
}

beforeEach(() => {
  vi.clearAllMocks()
  pinia = createPinia()
  setActivePinia(pinia)

  discoveryRepository.getCamerasAvailable.mockResolvedValue({ cameras: {} })
  discoveryRepository.getModelsAvailable.mockResolvedValue({ models: {} })
})

afterEach(() => {
  vi.useRealTimers()
})

function seedStore({ orchestratorOk = true, cameraOk = true, modelOk = true, activeConfigName = 'config_1' } = {}) {
  const store = useHealthStore()
  store.orchestratorOk = orchestratorOk
  store.cameraService = { ok: cameraOk }
  store.modelService = { ok: modelOk }
  store.activeConfigName = activeConfigName
}

describe('StatusBar', () => {
  it('renders VIO Cockpit title', async () => {
    seedStore()
    const wrapper = mountBar()
    await flushPromises()
    expect(wrapper.text()).toContain('VIO Cockpit')
  })

  it('shows Orchestrator chip', async () => {
    seedStore()
    const wrapper = mountBar()
    await flushPromises()
    expect(wrapper.text()).toContain('Orchestrator')
  })

  it('shows Camera and Model Server chips when store has services', async () => {
    seedStore()
    const wrapper = mountBar()
    await flushPromises()
    expect(wrapper.text()).toContain('Camera')
    expect(wrapper.text()).toContain('Model Server')
  })

  it('shows active config name inside Orchestrator dialog', async () => {
    seedStore({ activeConfigName: 'config_1' })
    const wrapper = mountBar()
    await flushPromises()
    const orchChip = wrapper.findAll('.v-chip').find((c) => c.text().includes('Orchestrator'))
    if (orchChip) {
      await orchChip.trigger('click')
      await flushPromises()
    }
    expect(wrapper.text()).toContain('config_1')
  })

  it('marks orchestrator chip as error when store orchestratorOk is false', async () => {
    seedStore({ orchestratorOk: false })
    const wrapper = mountBar()
    await flushPromises()
    expect(wrapper.text()).toContain('Orchestrator')
  })

  it('shows error icon for service chip when service is down', async () => {
    seedStore({ cameraOk: false })
    const wrapper = mountBar()
    await flushPromises()
    expect(wrapper.html()).toContain('mdi-alert-circle')
  })

  it('shows dash when no active config is set', async () => {
    seedStore({ activeConfigName: null })
    const wrapper = mountBar()
    await flushPromises()
    const orchChip = wrapper.findAll('.v-chip').find((c) => c.text().includes('Orchestrator'))
    if (orchChip) {
      await orchChip.trigger('click')
      await flushPromises()
    }
    expect(wrapper.text()).toContain('—')
  })

  it('hides Camera chip when store has no cameraService', async () => {
    const store = useHealthStore()
    store.orchestratorOk = true
    store.cameraService = null
    store.modelService = null
    const wrapper = mountBar()
    await flushPromises()
    expect(wrapper.text()).not.toContain('Camera')
    expect(wrapper.text()).not.toContain('Model Server')
  })

  it('calls getCamerasAvailable when opening camera dialog', async () => {
    seedStore()
    discoveryRepository.getCamerasAvailable.mockResolvedValue({
      cameras: { 'http://localhost:8001': { cam_1: {} } },
    })
    const wrapper = mountBar()
    await flushPromises()
    const cameraChip = wrapper.findAll('.v-chip').find((c) => c.text().includes('Camera'))
    if (cameraChip) {
      await cameraChip.trigger('click')
      await flushPromises()
    }
    expect(discoveryRepository.getCamerasAvailable).toHaveBeenCalledOnce()
  })
})
