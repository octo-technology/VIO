import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import { createPinia, setActivePinia } from 'pinia'
import { VueQueryPlugin, QueryClient } from '@tanstack/vue-query'
import TechnicianPage from '../TechnicianPage.vue'
import { useHealthStore } from '../../features/system-health/stores/healthStore'

vi.mock('../../features/station-config/api/configRepository', () => ({
  getConfigs: vi.fn(),
  activateConfig: vi.fn(),
  createConfig: vi.fn(),
  saveConfig: vi.fn(),
  deleteConfig: vi.fn(),
}))

vi.mock('../../features/station-config/api/discoveryRepository', () => ({
  getCamerasAvailable: vi.fn(),
  getModelsAvailable: vi.fn(),
  getConfigOptions: vi.fn(),
  getModelMetadata: vi.fn(),
}))

import * as configRepository from '../../features/station-config/api/configRepository'
import * as discoveryRepository from '../../features/station-config/api/discoveryRepository'

const vuetify = createVuetify({ components, directives })

let pinia
let queryClient

function mountView() {
  return mount(TechnicianPage, {
    global: {
      plugins: [vuetify, pinia, [VueQueryPlugin, { queryClient }]],
      stubs: {
        'v-dialog': { template: '<div v-if="modelValue"><slot /></div>', props: ['modelValue'] },
      },
    },
  })
}

const CONFIG_1 = {
  station_name: 'config_1',
  camera_configs: {
    camera_1: { camera_id: 'camera_1', camera_type: 'http', service_url: 'http://localhost:8001' },
    camera_2: { camera_id: 'camera_2', camera_type: 'http', service_url: 'http://localhost:8002' },
  },
  pipeline_steps: {
    step_1: {
      camera_id: 'camera_1',
      model_forwarder_config: { model_name: 'pin_detection', model_version: '1', model_serving_url: 'http://localhost:8501' },
      camera_rule_config: { camera_rule_type: 'expected_label_rule', expected_class: 'OK' },
    },
  },
  binary_storage_config: { storage_type: 'filesystem', target_directory: 'data_storage' },
  metadata_storage_config: { storage_type: 'filesystem', target_directory: 'data_storage' },
  item_rule_config: { item_rule_type: 'min_threshold_ratio_rule', expected_decision: 'OK', threshold: 0.8 },
}

const DISCOVERY_DEFAULTS = {
  cameras: { 'http://localhost:8001': { camera_1: { backend: 'usb', position: 'front' } } },
  models: { 'http://localhost:8501': ['pin_detection'] },
  options: { camera_rule_types: ['expected_label_rule', 'unexpected_label_rule', 'min_nb_objects_rule', 'max_nb_objects_rule'], item_rule_types: ['min_threshold_rule', 'min_threshold_ratio_rule'], storage_types: ['filesystem', 'gcs'], camera_types: ['http'] },
}

beforeEach(() => {
  vi.clearAllMocks()
  pinia = createPinia()
  setActivePinia(pinia)
  queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })

  // Seed store: config_1 is active
  const store = useHealthStore()
  store.activeConfigName = 'config_1'

  configRepository.getConfigs.mockResolvedValue([CONFIG_1])
  configRepository.activateConfig.mockResolvedValue(undefined)
  configRepository.createConfig.mockResolvedValue(undefined)
  configRepository.saveConfig.mockResolvedValue(undefined)
  configRepository.deleteConfig.mockResolvedValue(undefined)
  discoveryRepository.getCamerasAvailable.mockResolvedValue({ cameras: DISCOVERY_DEFAULTS.cameras })
  discoveryRepository.getModelsAvailable.mockResolvedValue({ models: DISCOVERY_DEFAULTS.models })
  discoveryRepository.getConfigOptions.mockResolvedValue(DISCOVERY_DEFAULTS.options)
  discoveryRepository.getModelMetadata.mockResolvedValue({ version: '1', class_names: ['OK', 'KO'], output_type: 'classification' })
})

describe('TechnicianView', () => {
  it('shows config list on mount', async () => {
    const wrapper = mountView()
    await flushPromises()
    expect(wrapper.text()).toContain('config_1')
  })

  it('shows active chip on the active config card', async () => {
    const wrapper = mountView()
    await flushPromises()
    expect(wrapper.text()).toContain('ACTIVE')
  })

  it('shows camera and step counts on config card', async () => {
    const wrapper = mountView()
    await flushPromises()
    expect(wrapper.text()).toContain('2 camera(s)')
    expect(wrapper.text()).toContain('1 pipeline step(s)')
  })

  it('shows empty state when no configs exist', async () => {
    configRepository.getConfigs.mockResolvedValue([])
    useHealthStore().activeConfigName = null
    const wrapper = mountView()
    await flushPromises()
    expect(wrapper.text()).toContain('No configurations yet')
  })

  it('enters edit mode on config card click', async () => {
    const wrapper = mountView()
    await flushPromises()
    const card = wrapper.findComponent({ name: 'VCard' })
    await card.trigger('click')
    await flushPromises()
    expect(wrapper.text()).toContain('Cameras')
    expect(wrapper.text()).toContain('Pipeline steps')
  })

  it('shows cameras in editor after clicking config card', async () => {
    const wrapper = mountView()
    await flushPromises()
    await wrapper.findComponent({ name: 'VCard' }).trigger('click')
    await flushPromises()

    const inputValues = wrapper.findAll('input').map((i) => i.element.value)
    expect(inputValues.some((v) => v.includes('localhost:8001'))).toBe(true)
  })

  it('shows pipeline steps in editor', async () => {
    const wrapper = mountView()
    await flushPromises()
    await wrapper.findComponent({ name: 'VCard' }).trigger('click')
    await flushPromises()

    const inputValues = wrapper.findAll('input').map((i) => i.element.value)
    expect(inputValues.some((v) => v === 'step_1')).toBe(true)
    expect(inputValues.some((v) => v.includes('pin_detection'))).toBe(true)
  })

  it('shows storage section in editor', async () => {
    const wrapper = mountView()
    await flushPromises()
    await wrapper.findComponent({ name: 'VCard' }).trigger('click')
    await flushPromises()
    expect(wrapper.text()).toContain('Storage')
  })

  it('calls activateConfig on Activate button click for non-active config', async () => {
    const CONFIG_2 = { ...CONFIG_1, station_name: 'config_2' }
    configRepository.getConfigs.mockResolvedValue([CONFIG_1, CONFIG_2])
    // config_1 is active, config_2 is not

    const wrapper = mountView()
    await flushPromises()

    // Find the Activate VBtn that is NOT disabled (belongs to non-active config)
    const activateBtns = wrapper.findAllComponents({ name: 'VBtn' }).filter((b) => b.text().includes('Activate'))
    const enabledBtn = activateBtns.find((b) => !b.props('disabled'))
    expect(enabledBtn).toBeDefined()
    await enabledBtn.trigger('click')
    await flushPromises()

    expect(configRepository.activateConfig).toHaveBeenCalledWith('config_2')
    // Store should be updated with new active config name
    expect(useHealthStore().activeConfigName).toBe('config_2')
  })

  it('shows delete confirmation dialog on delete click', async () => {
    const wrapper = mountView()
    await flushPromises()

    // Delete buttons are VBtn with color="error" — find via component prop
    const deleteBtns = wrapper.findAllComponents({ name: 'VBtn' }).filter((b) => b.props('color') === 'error')
    expect(deleteBtns.length).toBeGreaterThan(0)
    await deleteBtns[0].trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain('Supprimer')
  })

  it('adds a new step row on Add step click', async () => {
    const wrapper = mountView()
    await flushPromises()
    await wrapper.findComponent({ name: 'VCard' }).trigger('click')
    await flushPromises()

    const rowsBefore = wrapper.findAll('tbody').at(1)?.findAll('tr').length ?? 0
    const addBtn = wrapper.findAll('button').find((b) => b.text().includes('Add step'))
    await addBtn.trigger('click')
    await flushPromises()

    const rowsAfter = wrapper.findAll('tbody').at(1)?.findAll('tr').length ?? 0
    expect(rowsAfter).toBe(rowsBefore + 1)
  })

  it('adds a new camera row on Add camera click', async () => {
    const wrapper = mountView()
    await flushPromises()
    await wrapper.findComponent({ name: 'VCard' }).trigger('click')
    await flushPromises()

    const rowsBefore = wrapper.findAll('tbody').at(0)?.findAll('tr').length ?? 0
    const addBtn = wrapper.findAll('button').find((b) => b.text().includes('Add camera'))
    await addBtn.trigger('click')
    await flushPromises()

    const rowsAfter = wrapper.findAll('tbody').at(0)?.findAll('tr').length ?? 0
    expect(rowsAfter).toBe(rowsBefore + 1)
  })

  it('remove button is enabled when multiple cameras exist', async () => {
    const wrapper = mountView()
    await flushPromises()
    await wrapper.findComponent({ name: 'VCard' }).trigger('click')
    await flushPromises()

    const cameraRows = wrapper.findAll('tbody').at(0)?.findAll('tr') ?? []
    expect(cameraRows.length).toBe(2)
    for (const row of cameraRows) {
      const btn = row.find('button')
      expect(btn.attributes('disabled')).toBeUndefined()
    }
  })

  it('remove button is disabled when only one camera remains', async () => {
    configRepository.getConfigs.mockResolvedValue([{
      ...CONFIG_1,
      station_name: 'solo',
      camera_configs: { only_cam: { camera_id: 'only_cam', camera_type: 'http', service_url: '' } },
    }])
    useHealthStore().activeConfigName = 'solo'

    const wrapper = mountView()
    await flushPromises()
    await wrapper.findComponent({ name: 'VCard' }).trigger('click')
    await flushPromises()

    const cameraRows = wrapper.findAll('tbody').at(0)?.findAll('tr') ?? []
    expect(cameraRows.length).toBe(1)
    const deleteBtn = cameraRows[0].find('button')
    expect(deleteBtn.attributes('disabled')).toBeDefined()
  })

  it('shows expected_class input for expected_label_rule', async () => {
    const wrapper = mountView()
    await flushPromises()
    await wrapper.findComponent({ name: 'VCard' }).trigger('click')
    await flushPromises()

    const inputValues = wrapper.findAll('input').map((i) => i.element.value)
    expect(inputValues.some((v) => v === 'OK')).toBe(true)
  })

  it('clears camera rule when type set to none', async () => {
    const wrapper = mountView()
    await flushPromises()
    await wrapper.findComponent({ name: 'VCard' }).trigger('click')
    await flushPromises()

    const countOkBefore = wrapper.findAll('input').filter((i) => i.element.value === 'OK').length
    const selects = wrapper.findAllComponents({ name: 'VSelect' })
    const ruleSelect = selects.find((s) => s.props('modelValue') === 'expected_label_rule')
    await ruleSelect.vm.$emit('update:modelValue', 'none')
    await flushPromises()

    const countOkAfter = wrapper.findAll('input').filter((i) => i.element.value === 'OK').length
    expect(countOkAfter).toBeLessThan(countOkBefore)
  })

  it('sets default params when switching camera rule type', async () => {
    const wrapper = mountView()
    await flushPromises()
    await wrapper.findComponent({ name: 'VCard' }).trigger('click')
    await flushPromises()

    const selects = wrapper.findAllComponents({ name: 'VSelect' })
    const ruleSelect = selects.find((s) => s.props('modelValue') === 'expected_label_rule')
    await ruleSelect.vm.$emit('update:modelValue', 'min_nb_objects_rule')
    await flushPromises()

    const inputValues = wrapper.findAll('input').map((i) => i.element.value)
    expect(inputValues.some((v) => v === '1')).toBe(true)
  })

  it('shows item rule section in editor', async () => {
    const wrapper = mountView()
    await flushPromises()
    await wrapper.findComponent({ name: 'VCard' }).trigger('click')
    await flushPromises()
    expect(wrapper.text()).toContain('Item rule')
  })

  it('shows item rule threshold input', async () => {
    const wrapper = mountView()
    await flushPromises()
    await wrapper.findComponent({ name: 'VCard' }).trigger('click')
    await flushPromises()

    const inputValues = wrapper.findAll('input').map((i) => i.element.value)
    expect(inputValues.some((v) => v === '0.8')).toBe(true)
  })

  it('clears item rule when type set to none', async () => {
    const wrapper = mountView()
    await flushPromises()
    await wrapper.findComponent({ name: 'VCard' }).trigger('click')
    await flushPromises()

    const selects = wrapper.findAllComponents({ name: 'VSelect' })
    const itemRuleSelect = selects.find((s) => s.props('modelValue') === 'min_threshold_ratio_rule')
    await itemRuleSelect.vm.$emit('update:modelValue', 'none')
    await flushPromises()

    const inputValues = wrapper.findAll('input').map((i) => i.element.value)
    expect(inputValues.some((v) => v === '0.8')).toBe(false)
  })

  it('resets draft to original on Reset click', async () => {
    const wrapper = mountView()
    await flushPromises()
    await wrapper.findComponent({ name: 'VCard' }).trigger('click')
    await flushPromises()

    const selects = wrapper.findAllComponents({ name: 'VSelect' })
    const itemRuleSelect = selects.find((s) => s.props('modelValue') === 'min_threshold_ratio_rule')
    await itemRuleSelect.vm.$emit('update:modelValue', 'none')
    await flushPromises()

    const resetBtn = wrapper.findAll('button').find((b) => b.text() === 'Reset')
    await resetBtn.trigger('click')
    await flushPromises()

    const inputValues = wrapper.findAll('input').map((i) => i.element.value)
    expect(inputValues.some((v) => v === '0.8')).toBe(true)
  })
})
