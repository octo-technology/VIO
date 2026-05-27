import { ref, computed, nextTick, type Ref, type ComputedRef } from 'vue'
import { storeToRefs } from 'pinia'
import * as configRepository from '../api/configRepository'
import * as discoveryRepository from '../api/discoveryRepository'
import { useHealthStore } from '../../system-health/stores/healthStore'
import {
  RULE_TYPE_LABELS,
  OUTPUT_TYPE_CAMERA_RULES,
  createDefaultCameraRule,
} from '../domain/cameraRuleFactory'

interface ConfigOptions {
  camera_rule_types: string[]
  item_rule_types: string[]
  storage_types: string[]
  camera_types: string[]
}

interface ConfigEditorContext {
  configs: Ref<any[]>
  invalidateConfigs: () => Promise<void>
  cameraServiceUrls: ComputedRef<string[]>
  modelServerUrls: ComputedRef<string[]>
  configOptions: ComputedRef<ConfigOptions>
}

export function useConfigEditor({
  configs,
  invalidateConfigs,
  cameraServiceUrls,
  modelServerUrls,
  configOptions,
}: ConfigEditorContext) {
  const healthStore = useHealthStore()
  const { activeConfigName } = storeToRefs(healthStore)

  const mode = ref('list')
  const draft = ref<any>(null)
  const originalConfig = ref<any>(null)
  const isNewConfig = ref(false)
  const activating = ref<string | null>(null)
  const saving = ref(false)
  const deleting = ref(false)
  const snack = ref({ show: false, message: '', color: 'success' })
  const form = ref<any>(null)
  const nameField = ref<any>(null)
  const newConfigDialog = ref(false)
  const newConfigName = ref('')
  const newConfigNameForm = ref<any>(null)
  const deleteConfigDialog = ref(false)
  const configToDelete = ref<any>(null)
  const modelMetadataCache = ref<Record<string, any>>({})

  const itemRuleTypeItems = computed(() => [
    { title: 'None', value: 'none' },
    ...configOptions.value.item_rule_types.map((v: string) => ({ title: RULE_TYPE_LABELS[v] ?? v, value: v })),
  ])

  const storageTypeItems = computed(() => configOptions.value.storage_types)

  const isDirty = computed(() => {
    if (!draft.value) return false
    if (isNewConfig.value) return true
    if (!originalConfig.value) return true
    return JSON.stringify(draft.value) !== JSON.stringify(originalConfig.value)
  })

  const rules = {
    required: (v: any) => !!v || 'Required',
    url: (v: string) => { try { new URL(v); return true } catch { return 'Invalid URL' } },
    ratio: (v: any) => (v !== '' && Number(v) >= 0 && Number(v) <= 1) || 'Must be between 0 and 1',
    positiveInt: (v: any) => (Number.isInteger(Number(v)) && Number(v) >= 1) || 'Must be ≥ 1',
  }

  function uniqueCameraId(currentId: string) {
    return (v: string) => {
      if (!v) return 'Required'
      const others = Object.keys(draft.value.camera_configs).filter((k: string) => k !== currentId)
      return others.includes(v) ? 'Duplicate ID' : true
    }
  }

  function uniqueStepId(currentId: string) {
    return (v: string) => {
      if (!v) return 'Required'
      const others = Object.keys(draft.value.pipeline_steps).filter((k: string) => k !== currentId)
      return others.includes(v) ? 'Duplicate step ID' : true
    }
  }

  const uniqueNewConfigName = (v: string) => {
    if (!v) return 'Required'
    return configs.value.map((c: any) => c.station_name).includes(v) ? 'Ce nom existe déjà' : true
  }

  const uniqueEditableName = (v: string) => {
    if (!v) return 'Required'
    const exclude = isNewConfig.value ? null : originalConfig.value?.station_name
    return configs.value.map((c: any) => c.station_name).filter((n: string) => n !== exclude).includes(v)
      ? 'Ce nom existe déjà'
      : true
  }

  function notify(message: string, color = 'success') {
    snack.value = { show: true, message, color }
  }

  async function fetchModelMetadata(servingUrl: string, modelName: string, step: any = null) {
    if (!servingUrl || !modelName) return
    const key = `${servingUrl}::${modelName}`
    if (key in modelMetadataCache.value) {
      if (step && modelMetadataCache.value[key]?.version) {
        step.model_forwarder_config.model_version = modelMetadataCache.value[key].version
      }
      return
    }
    modelMetadataCache.value[key] = null
    try {
      const metadata = await discoveryRepository.getModelMetadata(servingUrl, modelName)
      modelMetadataCache.value[key] = metadata
      if (step && metadata.version) step.model_forwarder_config.model_version = metadata.version
    } catch {
      modelMetadataCache.value[key] = {}
    }
  }

  function classNamesForStep(step: any) {
    const url = step.model_forwarder_config?.model_serving_url
    const name = step.model_forwarder_config?.model_name
    if (!url || !name) return []
    return modelMetadataCache.value[`${url}::${name}`]?.class_names ?? []
  }

  async function fetchAllStepMetadata() {
    if (!draft.value) return
    for (const step of Object.values(draft.value.pipeline_steps)) {
      const s = step as any
      const url = s.model_forwarder_config?.model_serving_url
      const name = s.model_forwarder_config?.model_name
      if (url && name) fetchModelMetadata(url, name, s)
    }
  }

  async function onModelNameChange(step: any, name: string) {
    step.model_forwarder_config.model_name = name
    await fetchModelMetadata(step.model_forwarder_config.model_serving_url, name, step)
    _resetCameraRuleIfInvalid(step)
  }

  async function onServingUrlChange(step: any, url: string) {
    step.model_forwarder_config.model_serving_url = url
    await fetchModelMetadata(url, step.model_forwarder_config.model_name, step)
    _resetCameraRuleIfInvalid(step)
  }

  function cameraRuleItemsForStep(step: any) {
    const key = `${step.model_forwarder_config?.model_serving_url}::${step.model_forwarder_config?.model_name}`
    const outputType = modelMetadataCache.value[key]?.output_type
    const allowed = OUTPUT_TYPE_CAMERA_RULES[outputType]
    const toItem = (v: string) => ({ title: RULE_TYPE_LABELS[v] ?? v, value: v })
    const base = [{ title: 'None', value: 'none' }]
    return allowed
      ? [...base, ...allowed.map(toItem)]
      : [...base, ...configOptions.value.camera_rule_types.map(toItem)]
  }

  function _resetCameraRuleIfInvalid(step: any) {
    if (!step.camera_rule_config) return
    const key = `${step.model_forwarder_config?.model_serving_url}::${step.model_forwarder_config?.model_name}`
    const outputType = modelMetadataCache.value[key]?.output_type
    const allowed = OUTPUT_TYPE_CAMERA_RULES[outputType]
    if (allowed && !allowed.includes(step.camera_rule_config.camera_rule_type)) {
      step.camera_rule_config = null
    }
  }

  function startEdit(cfg: any) {
    originalConfig.value = cfg
    draft.value = JSON.parse(JSON.stringify(cfg))
    isNewConfig.value = false
    mode.value = 'edit'
    nextTick(() => {
      form.value?.resetValidation()
      fetchAllStepMetadata()
    })
  }

  function closeDraft() {
    draft.value = null
    originalConfig.value = null
    isNewConfig.value = false
    mode.value = 'list'
  }

  async function activateConfig(name: string) {
    activating.value = name
    try {
      await configRepository.activateConfig(name)
      await healthStore.poll()
      notify(`Config "${name}" activated`)
    } catch (e: any) {
      const detail = e?.response?.data?.detail
      notify(typeof detail === 'string' ? detail : 'Failed to activate config', 'error')
    } finally {
      activating.value = null
    }
  }

  function confirmDelete(cfg: any) {
    configToDelete.value = cfg
    deleteConfigDialog.value = true
  }

  async function deleteConfig() {
    deleting.value = true
    const name = configToDelete.value.station_name
    try {
      await configRepository.deleteConfig(name)
      deleteConfigDialog.value = false
      if (activeConfigName.value === name) healthStore.setActiveConfigName(null)
      await invalidateConfigs()
      notify(`Config "${name}" deleted`)
    } catch (e: any) {
      const detail = e?.response?.data?.detail
      notify(typeof detail === 'string' ? detail : 'Failed to delete config', 'error')
    } finally {
      deleting.value = false
    }
  }

  function createNewConfig() {
    const name = newConfigName.value.trim()
    draft.value = {
      station_name: name,
      camera_configs: {
        cam_1: { camera_id: 'cam_1', camera_type: 'http', service_url: cameraServiceUrls.value[0] ?? 'http://localhost:8001' },
      },
      pipeline_steps: {},
      binary_storage_config: { storage_type: 'filesystem', target_directory: 'data_storage' },
      metadata_storage_config: { storage_type: 'filesystem', target_directory: 'data_storage' },
    }
    originalConfig.value = null
    isNewConfig.value = true
    newConfigDialog.value = false
    newConfigName.value = ''
    mode.value = 'edit'
    nextTick(() => form.value?.resetValidation())
  }

  function resetDraft() {
    if (originalConfig.value) {
      draft.value = JSON.parse(JSON.stringify(originalConfig.value))
      nextTick(() => form.value?.resetValidation())
    }
  }

  async function saveConfig(): Promise<boolean> {
    const nameErrors = await (nameField.value?.validate() ?? Promise.resolve([]))
    const { valid: formValid } = await form.value.validate()
    if (nameErrors.length > 0 || !formValid) {
      notify('Please fix the errors before saving', 'error')
      return false
    }
    saving.value = true
    const newName = draft.value.station_name
    const oldName = originalConfig.value?.station_name ?? null
    const isRename = !isNewConfig.value && oldName && oldName !== newName
    try {
      if (isNewConfig.value) {
        await configRepository.createConfig(draft.value)
        isNewConfig.value = false
      } else {
        await configRepository.saveConfig(draft.value)
        if (isRename) {
          await configRepository.deleteConfig(oldName)
          if (activeConfigName.value === oldName) {
            await configRepository.activateConfig(newName)
            healthStore.setActiveConfigName(newName)
          }
        }
      }
      originalConfig.value = JSON.parse(JSON.stringify(draft.value))
      await invalidateConfigs()
      notify(`Config "${newName}" saved`)
      return true
    } catch (e: any) {
      const detail = e?.response?.data?.detail
      const message = Array.isArray(detail)
        ? detail.map((err: any) => err.msg ?? JSON.stringify(err)).join(' · ')
        : (detail ?? 'Failed to save config')
      notify(message, 'error')
      return false
    } finally {
      saving.value = false
    }
  }

  async function saveAndActivate() {
    const saved = await saveConfig()
    if (saved) await activateConfig(draft.value.station_name)
  }

  function onStorageTypeChange(storageConfig: any, newType: string) {
    storageConfig.storage_type = newType
    if (newType === 'filesystem') {
      storageConfig.bucket_name = null
    } else if (!storageConfig.bucket_name) {
      storageConfig.bucket_name = ''
    }
  }

  function setCameraRuleType(stepId: string, type: string) {
    draft.value.pipeline_steps[stepId].camera_rule_config = createDefaultCameraRule(type)
  }

  function setItemRuleType(type: string) {
    draft.value.item_rule_config =
      type === 'none' ? null : { item_rule_type: type, expected_decision: 'OK', threshold: 1 }
  }

  function addStep() {
    const newId = `step_${Object.keys(draft.value.pipeline_steps).length + 1}`
    const firstCamera = Object.keys(draft.value.camera_configs)[0] ?? ''
    const firstModelUrl = modelServerUrls.value[0] ?? ''
    draft.value.pipeline_steps = {
      ...draft.value.pipeline_steps,
      [newId]: {
        camera_id: firstCamera,
        model_forwarder_config: { model_name: '', model_version: '1', model_serving_url: firstModelUrl },
      },
    }
  }

  function removeStep(stepId: string) {
    const updated = { ...draft.value.pipeline_steps }
    delete updated[stepId]
    draft.value.pipeline_steps = updated
  }

  function renameStepId(oldId: string, newId: string) {
    if (!newId || newId === oldId) return
    const updated: Record<string, any> = {}
    for (const [k, v] of Object.entries(draft.value.pipeline_steps)) {
      updated[k === oldId ? newId : k] = v
    }
    draft.value.pipeline_steps = updated
  }

  function addCamera() {
    const newId = `camera_${Object.keys(draft.value.camera_configs).length + 1}`
    const firstUrl = cameraServiceUrls.value[0] ?? ''
    draft.value.camera_configs = {
      ...draft.value.camera_configs,
      [newId]: { camera_id: newId, camera_type: 'http', service_url: firstUrl },
    }
  }

  function removeCamera(camId: string) {
    const updated = { ...draft.value.camera_configs }
    delete updated[camId]
    draft.value.camera_configs = updated
  }

  function renameCameraId(oldId: string, newId: string) {
    if (!newId || newId === oldId) return
    const updated: Record<string, any> = {}
    for (const [k, v] of Object.entries(draft.value.camera_configs)) {
      updated[k === oldId ? newId : k] = k === oldId ? { ...(v as any), camera_id: newId } : v
    }
    draft.value.camera_configs = updated
    for (const step of Object.values(draft.value.pipeline_steps)) {
      if ((step as any).camera_id === oldId) (step as any).camera_id = newId
    }
  }

  return {
    mode,
    draft,
    originalConfig,
    isNewConfig,
    activating,
    saving,
    deleting,
    snack,
    form,
    nameField,
    newConfigDialog,
    newConfigName,
    newConfigNameForm,
    deleteConfigDialog,
    configToDelete,
    isDirty,
    itemRuleTypeItems,
    storageTypeItems,
    rules,
    uniqueCameraId,
    uniqueStepId,
    uniqueNewConfigName,
    uniqueEditableName,
    notify,
    startEdit,
    closeDraft,
    resetDraft,
    activateConfig,
    confirmDelete,
    deleteConfig,
    createNewConfig,
    saveConfig,
    saveAndActivate,
    onStorageTypeChange,
    setCameraRuleType,
    setItemRuleType,
    addStep,
    removeStep,
    renameStepId,
    addCamera,
    removeCamera,
    renameCameraId,
    modelMetadataCache,
    fetchModelMetadata,
    classNamesForStep,
    fetchAllStepMetadata,
    onModelNameChange,
    onServingUrlChange,
    cameraRuleItemsForStep,
  }
}
