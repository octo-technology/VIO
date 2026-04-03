import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import OperatorView from '../OperatorView.vue'

vi.mock('../../services/api', () => ({
  default: {
    getItems: vi.fn(),
    getItem: vi.fn(),
    trigger: vi.fn(),
    getActiveConfig: vi.fn(),
    getItemImage: vi.fn((itemId, cameraId) => `/api/v1/items/${itemId}/binaries/${cameraId}`),
  },
}))

import api from '../../services/api'

const vuetify = createVuetify({ components, directives })

function mountView({ attachToBody = false } = {}) {
  return mount(OperatorView, {
    global: { plugins: [vuetify] },
    ...(attachToBody ? { attachTo: document.body } : {}),
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
  pipeline_steps: {
    step_1: {
      camera_id: 'camera_1',
      camera_rule_config: { camera_rule_type: 'expected_label_rule', expected_class: 'OK' },
    },
  },
  item_rule_config: {
    item_rule_type: 'min_threshold_ratio_rule',
    expected_decision: 'OK',
    threshold: 0.75,
  },
}

beforeEach(() => {
  vi.clearAllMocks()
  api.getItems.mockResolvedValue({ data: [] })
  api.getItem.mockResolvedValue({ data: DONE_ITEM })
  api.trigger.mockResolvedValue({ data: { item_id: ITEM_ID } })
  api.getActiveConfig.mockResolvedValue({ data: STATION_CONFIG })
})

describe('OperatorView', () => {
  it('renders the trigger button', async () => {
    const wrapper = mountView()
    await flushPromises()
    expect(wrapper.text()).toContain('Trigger Inspection')
  })

  it('loads items and config on mount', async () => {
    api.getItems.mockResolvedValue({
      data: [{ id: ITEM_ID, state: 'DONE', decision: 'OK', creation_date: '2026-04-02T10:00:00' }],
    })
    mountView()
    await flushPromises()
    expect(api.getItems).toHaveBeenCalledOnce()
    expect(api.getActiveConfig).toHaveBeenCalledOnce()
  })

  it('does not show last inspection panel before trigger', async () => {
    const wrapper = mountView()
    await flushPromises()
    expect(wrapper.text()).not.toContain('Last Inspection')
  })

  it('calls trigger API and shows last inspection panel after click', async () => {
    const wrapper = mountView()
    await flushPromises()

    await wrapper.find('button').trigger('click')
    await flushPromises()

    expect(api.trigger).toHaveBeenCalledOnce()
    expect(api.getItem).toHaveBeenCalledWith(ITEM_ID)
    expect(wrapper.text()).toContain('Last Inspection')
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
    api.getItem.mockResolvedValue({ data: { ...DONE_ITEM, decision: 'KO' } })
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
    await flushPromises()

    expect(wrapper.text()).toContain('step_1')
    expect(wrapper.text()).toContain('95.0%')
  })

  it('continues polling when item not yet persisted (404)', async () => {
    vi.useFakeTimers()
    api.getItem
      .mockRejectedValueOnce(new Error('404'))
      .mockResolvedValue({ data: DONE_ITEM })

    const wrapper = mountView()
    await flushPromises()
    await wrapper.find('button').trigger('click')
    await flushPromises()

    await vi.advanceTimersByTimeAsync(600)
    await flushPromises()

    vi.useRealTimers()
    expect(api.getItem).toHaveBeenCalledTimes(2)
    expect(wrapper.text()).toContain('Last Inspection')
  })

  it('handles missing item_id in trigger response gracefully', async () => {
    api.trigger.mockResolvedValue({ data: {} })
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

    const wrapper = mountView()
    await flushPromises()
    await wrapper.find('button').trigger('click')
    await flushPromises()

    expect(consoleSpy).toHaveBeenCalledWith('Trigger failed:', expect.any(Error))
    expect(wrapper.text()).not.toContain('Last Inspection')
    consoleSpy.mockRestore()
  })

  it('reloads items list after trigger completes', async () => {
    const wrapper = mountView()
    await flushPromises()
    const callsBefore = api.getItems.mock.calls.length

    await wrapper.find('button').trigger('click')
    await flushPromises()

    expect(api.getItems.mock.calls.length).toBeGreaterThan(callsBefore)
  })

  it('opens detail dialog and fetches item when a row is clicked', async () => {
    api.getItems.mockResolvedValue({
      data: [{ id: ITEM_ID, state: 'DONE', decision: 'OK', creation_date: '2026-04-02T10:00:00' }],
    })
    const wrapper = mountView({ attachToBody: true })
    await flushPromises()

    const dataTable = wrapper.findComponent({ name: 'VDataTable' })
    await dataTable.vm.$emit('click:row', {}, { item: { id: ITEM_ID, decision: 'OK', creation_date: '2026-04-02T10:00:00' } })
    await flushPromises()

    expect(api.getItem).toHaveBeenCalledWith(ITEM_ID)
    expect(document.body.textContent).toContain(ITEM_ID)
    wrapper.unmount()
  })

  it('shows camera rule in natural language in detail dialog', async () => {
    api.getItems.mockResolvedValue({
      data: [{ id: ITEM_ID, state: 'DONE', decision: 'OK', creation_date: '2026-04-02T10:00:00' }],
    })
    const wrapper = mountView({ attachToBody: true })
    await flushPromises()

    const dataTable = wrapper.findComponent({ name: 'VDataTable' })
    await dataTable.vm.$emit('click:row', {}, { item: { id: ITEM_ID, decision: 'OK', creation_date: '2026-04-02T10:00:00' } })
    await flushPromises()

    expect(document.body.textContent).toContain('Expects class "OK"')
    wrapper.unmount()
  })

  it('shows item rule in natural language in detail dialog', async () => {
    api.getItems.mockResolvedValue({
      data: [{ id: ITEM_ID, state: 'DONE', decision: 'OK', creation_date: '2026-04-02T10:00:00' }],
    })
    const wrapper = mountView({ attachToBody: true })
    await flushPromises()

    const dataTable = wrapper.findComponent({ name: 'VDataTable' })
    await dataTable.vm.$emit('click:row', {}, { item: { id: ITEM_ID, decision: 'OK', creation_date: '2026-04-02T10:00:00' } })
    await flushPromises()

    expect(document.body.textContent).toContain('75% of cameras must return "OK"')
    wrapper.unmount()
  })
})
