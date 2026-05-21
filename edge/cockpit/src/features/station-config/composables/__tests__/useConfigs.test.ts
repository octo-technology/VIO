import { describe, it, expect, vi, beforeEach } from 'vitest'
import { defineComponent, h } from 'vue'
import { mount, flushPromises } from '@vue/test-utils'
import { VueQueryPlugin, QueryClient } from '@tanstack/vue-query'
import { useConfigs } from '../useConfigs'

vi.mock('../../api/configRepository', () => ({
  getConfigs: vi.fn(),
}))

import * as configRepository from '../../api/configRepository'

const CONFIG_1 = {
  station_name: 'config_1',
  camera_configs: {},
  pipeline_steps: {},
  binary_storage_config: { storage_type: 'filesystem', target_directory: '' },
  metadata_storage_config: { storage_type: 'filesystem', target_directory: '' },
}

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

describe('useConfigs', () => {
  it('returns empty array while loading', () => {
    ;(configRepository.getConfigs as ReturnType<typeof vi.fn>).mockReturnValue(new Promise(() => {}))
    const { result } = mountWithQuery(() => useConfigs())
    expect(result().configs.value).toEqual([])
  })

  it('returns configs from repository after query resolves', async () => {
    ;(configRepository.getConfigs as ReturnType<typeof vi.fn>).mockResolvedValue([CONFIG_1])
    const { result } = mountWithQuery(() => useConfigs())
    await flushPromises()
    expect(result().configs.value).toEqual([CONFIG_1])
  })

  it('exposes isLoading as true while fetching', () => {
    ;(configRepository.getConfigs as ReturnType<typeof vi.fn>).mockReturnValue(new Promise(() => {}))
    const { result } = mountWithQuery(() => useConfigs())
    expect(result().isLoading.value).toBe(true)
  })

  it('exposes isLoading as false after fetch', async () => {
    ;(configRepository.getConfigs as ReturnType<typeof vi.fn>).mockResolvedValue([CONFIG_1])
    const { result } = mountWithQuery(() => useConfigs())
    await flushPromises()
    expect(result().isLoading.value).toBe(false)
  })

  it('invalidate() triggers a refetch', async () => {
    ;(configRepository.getConfigs as ReturnType<typeof vi.fn>).mockResolvedValue([CONFIG_1])
    const { result } = mountWithQuery(() => useConfigs())
    await flushPromises()
    const callsBefore = (configRepository.getConfigs as ReturnType<typeof vi.fn>).mock.calls.length

    await result().invalidate()
    await flushPromises()

    expect((configRepository.getConfigs as ReturnType<typeof vi.fn>).mock.calls.length).toBeGreaterThan(callsBefore)
  })
})
