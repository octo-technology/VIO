import { computed } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import * as discoveryRepository from '../api/discoveryRepository'

export function useDiscovery() {
  const { data: camerasData } = useQuery({
    queryKey: ['cameras-available'],
    queryFn: discoveryRepository.getCamerasAvailable,
  })
  const discoveredCameras = computed(() => camerasData.value?.cameras ?? {})

  const { data: modelsData } = useQuery({
    queryKey: ['models-available'],
    queryFn: discoveryRepository.getModelsAvailable,
  })
  const discoveredModels = computed(() => modelsData.value?.models ?? {})

  const { data: configOptionsData } = useQuery({
    queryKey: ['config-options'],
    queryFn: discoveryRepository.getConfigOptions,
  })
  const configOptions = computed(
    () => configOptionsData.value ?? { camera_rule_types: [], item_rule_types: [], storage_types: [], camera_types: [] },
  )

  const cameraServiceUrls = computed(() => Object.keys(discoveredCameras.value))
  const modelServerUrls = computed(() => Object.keys(discoveredModels.value))

  function camerasForUrl(url: string) {
    return Object.keys(discoveredCameras.value[url] ?? {})
  }

  function cameraBackendForUrl(url: string, camId: string) {
    return (discoveredCameras.value[url] as any)?.[camId] ?? null
  }

  function modelsForUrl(url: string) {
    return (discoveredModels.value[url] as any) ?? []
  }

  return {
    discoveredCameras,
    discoveredModels,
    configOptions,
    cameraServiceUrls,
    modelServerUrls,
    camerasForUrl,
    cameraBackendForUrl,
    modelsForUrl,
  }
}
