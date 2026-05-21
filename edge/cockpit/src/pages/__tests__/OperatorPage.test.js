import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import { createPinia, setActivePinia } from 'pinia'
import { VueQueryPlugin, QueryClient } from '@tanstack/vue-query'
import OperatorPage from '../OperatorPage.vue'
import { useHealthStore } from '../../features/system-health/stores/healthStore'

vi.mock('../../features/inspection/api/inspectionRepository', () => ({
  __v_isRef: false,
  getItems: vi.fn(),
  getItem: vi.fn(),
  trigger: vi.fn(),
  getItemImageUrl: vi.fn((itemId, cameraId) => `/api/v1/items/${itemId}/binaries/${cameraId}`),
}))

import * as inspectionRepository from '../../features/inspection/api/inspectionRepository'

const vuetify = createVuetify({ components, directives })

let pinia
let queryClient

function mountView() {
  return mount(OperatorPage, {
    global: { plugins: [vuetify, pinia, [VueQueryPlugin, { queryClient }]] },
  })
}

const ITEM_ID = 'abc-123'
const DONE_ITEM = {
  id: ITEM_ID,
  state: 'DONE',
  decision: 'OK',
  creation_date: '2026-04-02T10:00:00',
  cameras_metadata: { camera_1: {} },
  predictions: {
    step_1: { prediction_type: 'class', label: 'OK', probability: 0.95 },
  },
}

const STATION_CONFIG = {
  station_name: 'test_config',
  camera_configs: { camera_1: { camera_id: 'camera_1', camera_type: 'http', service_url: 'http://localhost:8001' } },
  pipeline_steps: {
    step_1: {
      camera_id: 'camera_1',
      model_forwarder_config: { model_name: 'pin_detection', model_version: '1', model_serving_url: 'http://localhost:8501' },
      camera_rule_config: { camera_rule_type: 'expected_label_rule', expected_class: 'OK' },
    },
  },
  item_rule_config: {
    item_rule_type: 'min_threshold_ratio_rule',
    expected_decision: 'OK',
    threshold: 0.75,
  },
  binary_storage_config: { storage_type: 'filesystem', target_directory: 'data_storage' },
  metadata_storage_config: { storage_type: 'filesystem', target_directory: 'data_storage' },
}

beforeEach(() => {
  vi.clearAllMocks()
  pinia = createPinia()
  setActivePinia(pinia)
  queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })

  // Seed store with active config
  const store = useHealthStore()
  store.activeConfig = STATION_CONFIG
  store.activeConfigName = STATION_CONFIG.station_name

  inspectionRepository.getItems.mockResolvedValue([])
  inspectionRepository.getItem.mockResolvedValue(DONE_ITEM)
  inspectionRepository.trigger.mockResolvedValue({ item_id: ITEM_ID })
})

describe('OperatorView', () => {
  it('renders the trigger button', async () => {
    const wrapper = mountView()
    await flushPromises()
    expect(wrapper.text()).toContain('Trigger Inspection')
  })

  it('loads items on mount', async () => {
    inspectionRepository.getItems.mockResolvedValue([
      { id: ITEM_ID, state: 'DONE', decision: 'OK', creation_date: '2026-04-02T10:00:00' },
    ])
    mountView()
    await flushPromises()
    expect(inspectionRepository.getItems).toHaveBeenCalledOnce()
  })

  it('calls trigger API and switches to detail mode', async () => {
    const wrapper = mountView()
    await flushPromises()

    await wrapper.find('button').trigger('click')
    await flushPromises()

    expect(inspectionRepository.trigger).toHaveBeenCalledOnce()
    expect(inspectionRepository.getItem).toHaveBeenCalledWith(ITEM_ID)
    expect(wrapper.text()).toContain(ITEM_ID)
  })

  it('shows OK chip when inspection decision is OK', async () => {
    const wrapper = mountView()
    await flushPromises()
    await wrapper.find('button').trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain('OK')
  })

  it('shows KO chip when inspection decision is KO', async () => {
    inspectionRepository.getItem.mockResolvedValue({ ...DONE_ITEM, decision: 'KO' })
    const wrapper = mountView()
    await flushPromises()
    await wrapper.find('button').trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain('KO')
  })

  it('shows prediction result for classification step', async () => {
    const wrapper = mountView()
    await flushPromises()
    await wrapper.find('button').trigger('click')
    // Each await in the async chain (trigger → pollUntilDone → loadItems) needs a flush
    await flushPromises()
    await flushPromises()
    await flushPromises()

    expect(wrapper.text()).toContain('step_1')
    expect(wrapper.text()).toContain('95.0%')
  })

  it('continues polling when item not yet persisted (404)', async () => {
    vi.useFakeTimers()
    inspectionRepository.getItem
      .mockRejectedValueOnce(new Error('404'))
      .mockResolvedValue(DONE_ITEM)

    const wrapper = mountView()
    await flushPromises()
    await wrapper.find('button').trigger('click')
    await flushPromises()

    await vi.advanceTimersByTimeAsync(600)
    await flushPromises()

    vi.useRealTimers()
    expect(inspectionRepository.getItem).toHaveBeenCalledTimes(2)
    expect(wrapper.text()).toContain(ITEM_ID)
  })

  it('shows error state when trigger returns no item_id', async () => {
    inspectionRepository.trigger.mockResolvedValue({ item_id: '' })

    const wrapper = mountView()
    await flushPromises()
    await wrapper.find('button').trigger('click')
    await flushPromises()

    // Stays in list mode (detail mode not entered after failed trigger)
    expect(wrapper.text()).toContain('Trigger Inspection')
    expect(wrapper.text()).not.toContain('Pipeline results')
  })

  it('reloads items list after trigger completes', async () => {
    const wrapper = mountView()
    await flushPromises()
    const callsBefore = inspectionRepository.getItems.mock.calls.length

    await wrapper.find('button').trigger('click')
    await flushPromises()

    expect(inspectionRepository.getItems.mock.calls.length).toBeGreaterThan(callsBefore)
  })

  it('opens detail view and fetches item when a row is clicked', async () => {
    inspectionRepository.getItems.mockResolvedValue([
      { id: ITEM_ID, state: 'DONE', decision: 'OK', creation_date: '2026-04-02T10:00:00' },
    ])
    const wrapper = mountView()
    await flushPromises()

    const dataTable = wrapper.findComponent({ name: 'VDataTable' })
    await dataTable.vm.$emit('click:row', {}, { item: { id: ITEM_ID, decision: 'OK', creation_date: '2026-04-02T10:00:00' } })
    await flushPromises()

    expect(inspectionRepository.getItem).toHaveBeenCalledWith(ITEM_ID)
    expect(wrapper.text()).toContain(ITEM_ID)
  })

  it('shows camera rule in natural language in detail view', async () => {
    inspectionRepository.getItems.mockResolvedValue([
      { id: ITEM_ID, state: 'DONE', decision: 'OK', creation_date: '2026-04-02T10:00:00' },
    ])
    const wrapper = mountView()
    await flushPromises()

    const dataTable = wrapper.findComponent({ name: 'VDataTable' })
    await dataTable.vm.$emit('click:row', {}, { item: { id: ITEM_ID, decision: 'OK', creation_date: '2026-04-02T10:00:00' } })
    await flushPromises()

    expect(wrapper.text()).toContain('Expects "OK"')
  })

  it('shows item rule in natural language in detail view', async () => {
    inspectionRepository.getItems.mockResolvedValue([
      { id: ITEM_ID, state: 'DONE', decision: 'OK', creation_date: '2026-04-02T10:00:00' },
    ])
    const wrapper = mountView()
    await flushPromises()

    const dataTable = wrapper.findComponent({ name: 'VDataTable' })
    await dataTable.vm.$emit('click:row', {}, { item: { id: ITEM_ID, decision: 'OK', creation_date: '2026-04-02T10:00:00' } })
    await flushPromises()

    expect(wrapper.text()).toContain('75% of cameras must return "OK"')
  })

  it('shows warning when no active config in store', async () => {
    const store = useHealthStore()
    store.activeConfig = null
    store.activeConfigName = null
    const wrapper = mountView()
    await flushPromises()
    expect(wrapper.text()).toContain('Aucune configuration active')
  })
})
