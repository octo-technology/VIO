import { defineStore } from 'pinia'
import { ref } from 'vue'
import * as healthRepository from '../api/healthRepository'
import * as configRepository from '../../station-config/api/configRepository'
import type { StationConfig } from '../../../entities/station-config/dtos/StationConfigDto'

export const useHealthStore = defineStore('health', () => {
  const orchestratorOk = ref(false)
  const cameraService = ref<{ ok: boolean } | null>(null)
  const modelService = ref<{ ok: boolean } | null>(null)
  const activeConfigName = ref<string | null>(null)
  const activeConfig = ref<StationConfig | null>(null)

  async function poll() {
    const [liveRes, servicesRes, configRes] = await Promise.allSettled([
      healthRepository.getLiveness(),
      healthRepository.getServicesHealth(),
      configRepository.getActiveConfig(),
    ])

    orchestratorOk.value = liveRes.status === 'fulfilled' && liveRes.value === true

    if (servicesRes.status === 'fulfilled') {
      cameraService.value = null
      modelService.value = null
      for (const info of Object.values(servicesRes.value.services)) {
        if (info.service_type === 'camera') cameraService.value = { ok: info.ok }
        else if (info.service_type === 'model_server') modelService.value = { ok: info.ok }
      }
    }

    if (configRes.status === 'fulfilled') {
      activeConfig.value = configRes.value
      activeConfigName.value = configRes.value?.station_name ?? null
    }
  }

  let timer: ReturnType<typeof setInterval> | null = null

  function startPolling() {
    poll()
    timer = setInterval(poll, 5000)
  }

  function stopPolling() {
    if (timer !== null) { clearInterval(timer); timer = null }
  }

  function setActiveConfigName(name: string | null) {
    activeConfigName.value = name
    if (name === null) activeConfig.value = null
  }

  return {
    orchestratorOk,
    cameraService,
    modelService,
    activeConfigName,
    activeConfig,
    poll,
    startPolling,
    stopPolling,
    setActiveConfigName,
  }
})
