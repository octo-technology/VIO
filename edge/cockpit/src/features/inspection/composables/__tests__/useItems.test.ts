import { describe, it, expect, vi, beforeEach } from 'vitest'
import { defineComponent, h } from 'vue'
import { mount, flushPromises } from '@vue/test-utils'
import { VueQueryPlugin, QueryClient } from '@tanstack/vue-query'
import { useItems } from '../useItems'

vi.mock('../../api/inspectionRepository', () => ({
  getItems: vi.fn(),
  getItem: vi.fn(),
  getItemImageUrl: vi.fn(),
}))

import * as inspectionRepository from '../../api/inspectionRepository'

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
})

describe('useItems', () => {
  it('returns empty array while loading', () => {
    ;(inspectionRepository.getItems as ReturnType<typeof vi.fn>).mockReturnValue(new Promise(() => {}))
    const { result } = mountWithQuery(() => useItems())
    expect(result().items.value).toEqual([])
  })

  it('returns items from repository after query resolves', async () => {
    const items = [{ id: 'abc', state: 'DONE', decision: 'OK', creation_date: '2026-01-01' }]
    ;(inspectionRepository.getItems as ReturnType<typeof vi.fn>).mockResolvedValue(items)
    const { result } = mountWithQuery(() => useItems())
    await flushPromises()
    expect(result().items.value).toEqual(items)
  })

  it('exposes isLoading as true during fetch', () => {
    ;(inspectionRepository.getItems as ReturnType<typeof vi.fn>).mockReturnValue(new Promise(() => {}))
    const { result } = mountWithQuery(() => useItems())
    expect(result().isLoading.value).toBe(true)
  })

  it('exposes isLoading as false after fetch completes', async () => {
    ;(inspectionRepository.getItems as ReturnType<typeof vi.fn>).mockResolvedValue([])
    const { result } = mountWithQuery(() => useItems())
    await flushPromises()
    expect(result().isLoading.value).toBe(false)
  })

  it('exposes a refetch function', () => {
    ;(inspectionRepository.getItems as ReturnType<typeof vi.fn>).mockResolvedValue([])
    const { result } = mountWithQuery(() => useItems())
    expect(typeof result().refetch).toBe('function')
  })

  it('fetchItem delegates to inspectionRepository.getItem and returns its result', async () => {
    ;(inspectionRepository.getItems as ReturnType<typeof vi.fn>).mockResolvedValue([])
    const item = { id: 'xyz', state: 'DONE', decision: 'OK', creation_date: '2026-01-01' }
    ;(inspectionRepository.getItem as ReturnType<typeof vi.fn>).mockResolvedValue(item)
    const { result } = mountWithQuery(() => useItems())
    const returned = await result().fetchItem('xyz')
    expect(inspectionRepository.getItem).toHaveBeenCalledWith('xyz')
    expect(returned).toEqual(item)
  })

  it('itemImageUrl delegates to inspectionRepository.getItemImageUrl and returns its result', () => {
    ;(inspectionRepository.getItems as ReturnType<typeof vi.fn>).mockResolvedValue([])
    ;(inspectionRepository.getItemImageUrl as ReturnType<typeof vi.fn>).mockReturnValue('http://api/items/xyz/binaries/cam_1')
    const { result } = mountWithQuery(() => useItems())
    const url = result().itemImageUrl('xyz', 'cam_1')
    expect(inspectionRepository.getItemImageUrl).toHaveBeenCalledWith('xyz', 'cam_1')
    expect(url).toBe('http://api/items/xyz/binaries/cam_1')
  })
})
