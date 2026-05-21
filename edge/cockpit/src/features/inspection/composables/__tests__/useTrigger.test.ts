import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { defineComponent, h } from 'vue'
import { mount, flushPromises } from '@vue/test-utils'
import { VueQueryPlugin, QueryClient } from '@tanstack/vue-query'
import { useTrigger } from '../useTrigger'

vi.mock('../../api/inspectionRepository', () => ({
  getItems: vi.fn(),
  getItem: vi.fn(),
  trigger: vi.fn(),
}))

import * as inspectionRepository from '../../api/inspectionRepository'

const ITEM_ID = 'item-123'
const DONE_ITEM = { id: ITEM_ID, state: 'DONE', decision: 'OK', creation_date: '2026-01-01', cameras_metadata: {}, predictions: {} }

function mountWithQuery(composableFn: () => any) {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  let result: any
  const Wrapper = defineComponent({
    setup() {
      result = composableFn()
      return () => h('div')
    },
  })
  mount(Wrapper, { global: { plugins: [[VueQueryPlugin, { queryClient }]] } })
  return { result: () => result, queryClient }
}

beforeEach(() => {
  vi.clearAllMocks()
  ;(inspectionRepository.trigger as ReturnType<typeof vi.fn>).mockResolvedValue({ item_id: ITEM_ID })
  ;(inspectionRepository.getItem as ReturnType<typeof vi.fn>).mockResolvedValue(DONE_ITEM)
})

afterEach(() => {
  vi.useRealTimers()
})

describe('useTrigger', () => {
  it('starts with triggering and polling false', () => {
    const { result } = mountWithQuery(() => useTrigger())
    expect(result().triggering.value).toBe(false)
    expect(result().polling.value).toBe(false)
  })

  it('calls trigger repository and invokes onPending with item_id', async () => {
    const { result } = mountWithQuery(() => useTrigger())
    const onPending = vi.fn()
    const onUpdate = vi.fn()
    await result().triggerInspection({ onPending, onUpdate })
    expect(inspectionRepository.trigger).toHaveBeenCalledOnce()
    expect(onPending).toHaveBeenCalledWith(ITEM_ID)
  })

  it('calls getItem and invokes onUpdate with item data', async () => {
    const { result } = mountWithQuery(() => useTrigger())
    const onUpdate = vi.fn()
    await result().triggerInspection({ onPending: vi.fn(), onUpdate })
    expect(inspectionRepository.getItem).toHaveBeenCalledWith(ITEM_ID)
    expect(onUpdate).toHaveBeenCalledWith(DONE_ITEM)
  })

  it('throws when trigger returns empty item_id', async () => {
    ;(inspectionRepository.trigger as ReturnType<typeof vi.fn>).mockResolvedValue({ item_id: '' })
    const { result } = mountWithQuery(() => useTrigger())
    await expect(result().triggerInspection({ onPending: vi.fn(), onUpdate: vi.fn() }))
      .rejects.toThrow('No item_id')
  })

  it('continues polling when getItem rejects once (404)', async () => {
    vi.useFakeTimers()
    ;(inspectionRepository.getItem as ReturnType<typeof vi.fn>)
      .mockRejectedValueOnce(new Error('404'))
      .mockResolvedValue(DONE_ITEM)

    const { result } = mountWithQuery(() => useTrigger())
    const promise = result().triggerInspection({ onPending: vi.fn(), onUpdate: vi.fn() })

    await vi.advanceTimersByTimeAsync(600)
    await flushPromises()
    await promise

    expect(inspectionRepository.getItem).toHaveBeenCalledTimes(2)
  })

  it('invalidates items query on completion', async () => {
    const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
    const invalidateSpy = vi.spyOn(queryClient, 'invalidateQueries')
    let result: any
    const Wrapper = defineComponent({
      setup() { result = useTrigger(); return () => h('div') },
    })
    mount(Wrapper, { global: { plugins: [[VueQueryPlugin, { queryClient }]] } })

    await result.triggerInspection({ onPending: vi.fn(), onUpdate: vi.fn() })
    expect(invalidateSpy).toHaveBeenCalledWith({ queryKey: ['items'] })
  })
})
