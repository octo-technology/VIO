import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import TechnicianView from '../TechnicianView.vue'

vi.mock('../../services/api', () => ({
  default: {
    getConfigs: vi.fn(),
    getActiveConfig: vi.fn(),
    setActiveConfig: vi.fn(),
  },
}))

import api from '../../services/api'

const vuetify = createVuetify({ components, directives })

function mountView() {
  return mount(TechnicianView, {
    global: { plugins: [vuetify] },
  })
}

const CONFIG_1 = {
  station_name: 'config_1',
  camera_configs: {
    camera_1: { camera_id: 'camera_1', camera_type: 'http', position: 'front', service_url: 'http://localhost:8001' },
    camera_2: { camera_id: 'camera_2', camera_type: 'http', position: 'back', service_url: 'http://localhost:8002' },
  },
  pipeline_steps: {
    step_1: {
      camera_id: 'camera_1',
      model_forwarder_config: { model_name: 'pin_detection', model_version: '1', model_serving_url: 'http://localhost:8501/', model_id: 'pin_detection_1' },
    },
  },
  binary_storage_config: { storage_type: 'filesystem', target_directory: 'data_storage' },
  metadata_storage_config: { storage_type: 'filesystem', target_directory: 'data_storage' },
}

const CONFIGS_RESPONSE = { config_1: CONFIG_1 }

beforeEach(() => {
  vi.clearAllMocks()
  api.getConfigs.mockResolvedValue({ data: CONFIGS_RESPONSE })
  api.getActiveConfig.mockResolvedValue({ data: { station_name: 'config_1' } })
  api.setActiveConfig.mockResolvedValue({ data: CONFIG_1 })
})

describe('TechnicianView', () => {
  it('shows config list on mount', async () => {
    const wrapper = mountView()
    await flushPromises()
    expect(wrapper.text()).toContain('config_1')
  })

  it('auto-selects active config on mount', async () => {
    const wrapper = mountView()
    await flushPromises()
    expect(wrapper.text()).toContain('Cameras')
    expect(wrapper.text()).toContain('Pipeline steps')
  })

  it('shows cameras in the editor', async () => {
    const wrapper = mountView()
    await flushPromises()
    expect(wrapper.text()).toContain('camera_1')
    const inputValues = wrapper.findAll('input').map((i) => i.element.value)
    expect(inputValues.some((v) => v.includes('localhost:8001'))).toBe(true)
  })

  it('shows pipeline steps in the editor', async () => {
    const wrapper = mountView()
    await flushPromises()
    const inputValues = wrapper.findAll('input').map((i) => i.element.value)
    expect(inputValues.some((v) => v === 'step_1')).toBe(true)
    expect(inputValues.some((v) => v.includes('pin_detection'))).toBe(true)
  })

  it('shows storage fields', async () => {
    const wrapper = mountView()
    await flushPromises()
    expect(wrapper.text()).toContain('Binary storage path')
    expect(wrapper.text()).toContain('Metadata storage path')
  })

  it('shows empty state when no config selected', async () => {
    api.getActiveConfig.mockResolvedValue({ data: {} })
    const wrapper = mountView()
    await flushPromises()
    expect(wrapper.text()).toContain('Select a configuration')
  })

  it('calls setActiveConfig with full config object on Apply', async () => {
    const wrapper = mountView()
    await flushPromises()

    const applyBtn = wrapper.findAll('button').find((b) => b.text().includes('Apply'))
    await applyBtn.trigger('click')
    await flushPromises()

    expect(api.setActiveConfig).toHaveBeenCalledWith(expect.objectContaining({ station_name: 'config_1' }))
  })

  it('shows success snackbar after Apply', async () => {
    const wrapper = mount(TechnicianView, {
      global: { plugins: [vuetify] },
      attachTo: document.body,
    })
    await flushPromises()

    const applyBtn = wrapper.findAll('button').find((b) => b.text().includes('Apply'))
    await applyBtn.trigger('click')
    await flushPromises()

    expect(document.body.textContent).toContain('applied successfully')
    wrapper.unmount()
  })

  it('shows error snackbar when Apply fails', async () => {
    api.setActiveConfig.mockRejectedValue({ response: { data: { detail: 'Invalid config' } } })
    const wrapper = mount(TechnicianView, {
      global: { plugins: [vuetify] },
      attachTo: document.body,
    })
    await flushPromises()

    const applyBtn = wrapper.findAll('button').find((b) => b.text().includes('Apply'))
    await applyBtn.trigger('click')
    await flushPromises()

    expect(document.body.textContent).toContain('Invalid config')
    wrapper.unmount()
  })

  it('adds a new step row on Add step click', async () => {
    const wrapper = mountView()
    await flushPromises()

    // pipeline steps table is the second tbody
    const rowsBefore = wrapper.findAll('tbody').at(1).findAll('tr').length
    const addBtn = wrapper.findAll('button').find((b) => b.text().includes('Add step'))
    await addBtn.trigger('click')
    await flushPromises()

    const rowsAfter = wrapper.findAll('tbody').at(1).findAll('tr').length
    expect(rowsAfter).toBe(rowsBefore + 1)
  })

  it('pre-selects first camera when adding a new step', async () => {
    const wrapper = mountView()
    await flushPromises()

    const addBtn = wrapper.findAll('button').find((b) => b.text().includes('Add step'))
    await addBtn.trigger('click')
    await flushPromises()

    // New step row should reference the first camera
    const stepSelects = wrapper.findAll('tbody').at(1).findAllComponents({ name: 'VSelect' })
    const cameraSelects = stepSelects.filter((s) => Object.keys(CONFIG_1.camera_configs).includes(s.props('modelValue')))
    expect(cameraSelects.length).toBeGreaterThan(0)
  })

  it('resets draft to original on Reset click', async () => {
    const wrapper = mountView()
    await flushPromises()

    // find the service_url input and change it
    const inputs = wrapper.findAll('input')
    const urlInput = inputs.find((i) => i.element.value.includes('localhost:8001'))
    await urlInput.setValue('http://new-url:9999')

    const resetBtn = wrapper.findAll('button').find((b) => b.text() === 'Reset')
    await resetBtn.trigger('click')
    await flushPromises()

    const inputValues = wrapper.findAll('input').map((i) => i.element.value)
    expect(inputValues.some((v) => v.includes('localhost:8001'))).toBe(true)
  })

  it('adds a new camera row on Add camera click', async () => {
    const wrapper = mountView()
    await flushPromises()

    // camera table is the first tbody
    const rowsBefore = wrapper.findAll('tbody').at(0).findAll('tr').length
    const addBtn = wrapper.findAll('button').find((b) => b.text().includes('Add camera'))
    await addBtn.trigger('click')
    await flushPromises()

    const rowsAfter = wrapper.findAll('tbody').at(0).findAll('tr').length
    expect(rowsAfter).toBe(rowsBefore + 1)
  })

  it('remove button is enabled when multiple cameras exist', async () => {
    const wrapper = mountView()
    await flushPromises()

    // Camera table is first tbody — 2 cameras → delete buttons enabled
    const cameraRows = wrapper.findAll('tbody').at(0).findAll('tr')
    expect(cameraRows.length).toBe(2)
    for (const row of cameraRows) {
      const btn = row.find('button')
      expect(btn.attributes('disabled')).toBeUndefined()
    }
  })

  it('remove button is disabled when only one camera remains', async () => {
    api.getConfigs.mockResolvedValue({
      data: {
        solo: {
          ...CONFIG_1,
          station_name: 'solo',
          camera_configs: {
            only_cam: { camera_id: 'only_cam', camera_type: 'http', position: '', service_url: '' },
          },
        },
      },
    })
    api.getActiveConfig.mockResolvedValue({ data: { station_name: 'solo' } })

    const wrapper = mountView()
    await flushPromises()

    // The delete button should be disabled (only one camera)
    const cameraRows = wrapper.findAll('tbody').at(0).findAll('tr')
    expect(cameraRows.length).toBe(1)
    const deleteBtn = cameraRows[0].find('button')
    expect(deleteBtn.attributes('disabled')).toBeDefined()
  })
})
