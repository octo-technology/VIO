import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useHealthStore } from '../healthStore'

vi.mock('../../api/healthRepository', () => ({
  getLiveness: vi.fn(),
  getServicesHealth: vi.fn(),
}))

vi.mock('../../../../features/station-config/api/configRepository', () => ({
  getActiveConfig: vi.fn(),
}))

import * as healthRepository from '../../api/healthRepository'
import * as configRepository from '../../../../features/station-config/api/configRepository'

const SERVICES_HEALTH = {
  services: {
    'http://localhost:8001': { service_type: 'camera', ok: true },
    'http://localhost:8501': { service_type: 'model_server', ok: true },
  },
}

const STATION_CONFIG = {
  station_name: 'config_1',
  camera_configs: {},
  pipeline_steps: {},
  binary_storage_config: { storage_type: 'filesystem', target_directory: '' },
  metadata_storage_config: { storage_type: 'filesystem', target_directory: '' },
}

beforeEach(() => {
  setActivePinia(createPinia())
  vi.clearAllMocks()
  ;(healthRepository.getLiveness as ReturnType<typeof vi.fn>).mockResolvedValue(true)
  ;(healthRepository.getServicesHealth as ReturnType<typeof vi.fn>).mockResolvedValue(SERVICES_HEALTH)
  ;(configRepository.getActiveConfig as ReturnType<typeof vi.fn>).mockResolvedValue(STATION_CONFIG)
})

afterEach(() => {
  vi.useRealTimers()
})

describe('healthStore', () => {
  it('initialises with safe defaults', () => {
    const store = useHealthStore()
    expect(store.orchestratorOk).toBe(false)
    expect(store.cameraService).toBeNull()
    expect(store.modelService).toBeNull()
    expect(store.activeConfigName).toBeNull()
    expect(store.activeConfig).toBeNull()
  })

  it('poll() sets orchestratorOk from liveness', async () => {
    const store = useHealthStore()
    await store.poll()
    expect(store.orchestratorOk).toBe(true)
  })

  it('poll() sets orchestratorOk to false when liveness returns false', async () => {
    ;(healthRepository.getLiveness as ReturnType<typeof vi.fn>).mockResolvedValue(false)
    const store = useHealthStore()
    await store.poll()
    expect(store.orchestratorOk).toBe(false)
  })

  it('poll() sets cameraService and modelService from services health', async () => {
    const store = useHealthStore()
    await store.poll()
    expect(store.cameraService).toEqual({ ok: true })
    expect(store.modelService).toEqual({ ok: true })
  })

  it('poll() sets activeConfigName and activeConfig from getActiveConfig', async () => {
    const store = useHealthStore()
    await store.poll()
    expect(store.activeConfigName).toBe('config_1')
    expect(store.activeConfig).toEqual(STATION_CONFIG)
  })

  it('poll() sets activeConfigName to null when getActiveConfig returns null', async () => {
    ;(configRepository.getActiveConfig as ReturnType<typeof vi.fn>).mockResolvedValue(null)
    const store = useHealthStore()
    await store.poll()
    expect(store.activeConfigName).toBeNull()
    expect(store.activeConfig).toBeNull()
  })

  it('poll() does not crash when liveness rejects', async () => {
    ;(healthRepository.getLiveness as ReturnType<typeof vi.fn>).mockRejectedValue(new Error('net'))
    const store = useHealthStore()
    await store.poll()
    expect(store.orchestratorOk).toBe(false)
  })

  it('poll() does not update services when getServicesHealth rejects', async () => {
    ;(healthRepository.getServicesHealth as ReturnType<typeof vi.fn>).mockRejectedValue(new Error('net'))
    const store = useHealthStore()
    await store.poll()
    expect(store.cameraService).toBeNull()
    expect(store.modelService).toBeNull()
  })

  it('startPolling() calls poll immediately then on interval', async () => {
    vi.useFakeTimers()
    const store = useHealthStore()
    store.startPolling()
    await vi.runAllTicks()
    const callsAfterStart = (healthRepository.getLiveness as ReturnType<typeof vi.fn>).mock.calls.length

    await vi.advanceTimersByTimeAsync(5000)
    await vi.runAllTicks()

    expect((healthRepository.getLiveness as ReturnType<typeof vi.fn>).mock.calls.length).toBeGreaterThan(callsAfterStart)
    store.stopPolling()
  })

  it('stopPolling() prevents further polls', async () => {
    vi.useFakeTimers()
    const store = useHealthStore()
    store.startPolling()
    await vi.runAllTicks()
    store.stopPolling()

    const callsBefore = (healthRepository.getLiveness as ReturnType<typeof vi.fn>).mock.calls.length
    await vi.advanceTimersByTimeAsync(10000)
    await vi.runAllTicks()

    expect((healthRepository.getLiveness as ReturnType<typeof vi.fn>).mock.calls.length).toBe(callsBefore)
  })

  it('setActiveConfigName() updates activeConfigName', () => {
    const store = useHealthStore()
    store.setActiveConfigName('new_config')
    expect(store.activeConfigName).toBe('new_config')
  })

  it('setActiveConfigName(null) clears activeConfig too', () => {
    const store = useHealthStore()
    store['activeConfig'] = STATION_CONFIG as any
    store.setActiveConfigName(null)
    expect(store.activeConfig).toBeNull()
  })
})
