import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { ref, computed } from 'vue'
import { useConfigEditor } from '../useConfigEditor'

vi.mock('../../api/configRepository', () => ({
  activateConfig: vi.fn(),
  createConfig: vi.fn(),
  saveConfig: vi.fn(),
  deleteConfig: vi.fn(),
  getActiveConfig: vi.fn(),
}))

vi.mock('../../api/discoveryRepository', () => ({
  getModelMetadata: vi.fn(),
}))

vi.mock('../../../system-health/api/healthRepository', () => ({
  getLiveness: vi.fn(),
  getServicesHealth: vi.fn(),
}))

import * as configRepository from '../../api/configRepository'

const STORAGE = { storage_type: 'filesystem', target_directory: 'data' }

const CONFIG_1 = {
  station_name: 'config_1',
  camera_configs: {
    cam_1: { camera_id: 'cam_1', camera_type: 'http', service_url: 'http://localhost:8001' },
  },
  pipeline_steps: {
    step_1: {
      camera_id: 'cam_1',
      model_forwarder_config: { model_name: 'model', model_serving_url: 'http://localhost:8501' },
    },
  },
  binary_storage_config: { ...STORAGE },
  metadata_storage_config: { ...STORAGE },
}

function makeContext(overrides: any = {}) {
  return {
    configs: ref([CONFIG_1]),
    invalidateConfigs: vi.fn().mockResolvedValue(undefined),
    cameraServiceUrls: computed(() => ['http://localhost:8001']),
    modelServerUrls: computed(() => ['http://localhost:8501']),
    configOptions: computed(() => ({
      camera_rule_types: ['expected_label_rule', 'unexpected_label_rule'],
      item_rule_types: ['min_threshold_rule', 'min_threshold_ratio_rule'],
      storage_types: ['filesystem', 'gcs'],
      camera_types: ['http'],
    })),
    ...overrides,
  }
}

function setup(ctxOverrides: any = {}) {
  const ctx = makeContext(ctxOverrides)
  const editor = useConfigEditor(ctx as any)
  return { editor, ctx }
}

beforeEach(() => {
  setActivePinia(createPinia())
  vi.clearAllMocks()
  ;(configRepository.activateConfig as ReturnType<typeof vi.fn>).mockResolvedValue(undefined)
  ;(configRepository.createConfig as ReturnType<typeof vi.fn>).mockResolvedValue(undefined)
  ;(configRepository.saveConfig as ReturnType<typeof vi.fn>).mockResolvedValue(undefined)
  ;(configRepository.deleteConfig as ReturnType<typeof vi.fn>).mockResolvedValue(undefined)
  ;(configRepository.getActiveConfig as ReturnType<typeof vi.fn>).mockResolvedValue(null)
})

// ─── isDirty ────────────────────────────────────────────────────────────────

describe('isDirty', () => {
  it('is false when there is no draft', () => {
    const { editor } = setup()
    expect(editor.isDirty.value).toBe(false)
  })

  it('is false immediately after startEdit (draft matches original)', () => {
    const { editor } = setup()
    editor.startEdit(CONFIG_1)
    expect(editor.isDirty.value).toBe(false)
  })

  it('is true after startEdit when draft is mutated', () => {
    const { editor } = setup()
    editor.startEdit(CONFIG_1)
    editor.draft.value.station_name = 'changed'
    expect(editor.isDirty.value).toBe(true)
  })

  it('is true when isNewConfig is true', () => {
    const ctx = makeContext()
    ctx.configs = ref([])
    const editor = useConfigEditor(ctx as any)
    editor.newConfigName.value = 'new_station'
    editor.createNewConfig()
    expect(editor.isDirty.value).toBe(true)
  })
})

// ─── Validation: uniqueNewConfigName ────────────────────────────────────────

describe('uniqueNewConfigName', () => {
  it('returns true for a name not already taken', () => {
    const { editor } = setup()
    expect(editor.uniqueNewConfigName('brand_new')).toBe(true)
  })

  it('returns an error string when name already exists', () => {
    const { editor } = setup()
    expect(editor.uniqueNewConfigName('config_1')).not.toBe(true)
  })

  it('returns an error string for empty input', () => {
    const { editor } = setup()
    expect(editor.uniqueNewConfigName('')).not.toBe(true)
  })
})

// ─── Validation: uniqueEditableName ─────────────────────────────────────────

describe('uniqueEditableName', () => {
  it('returns true for a name not taken by any other config', () => {
    const { editor } = setup()
    editor.startEdit(CONFIG_1)
    expect(editor.uniqueEditableName('totally_new')).toBe(true)
  })

  it('returns true for the original name of the config being edited (self-exclude)', () => {
    const { editor } = setup()
    editor.startEdit(CONFIG_1)
    expect(editor.uniqueEditableName('config_1')).toBe(true)
  })

  it('returns an error string when name is taken by another config', () => {
    const ctx = makeContext()
    ctx.configs = ref([CONFIG_1, { ...CONFIG_1, station_name: 'config_2' }])
    const editor = useConfigEditor(ctx as any)
    editor.startEdit(CONFIG_1)
    expect(editor.uniqueEditableName('config_2')).not.toBe(true)
  })
})

// ─── Validation: uniqueCameraId / uniqueStepId ───────────────────────────────

describe('uniqueCameraId', () => {
  it('returns true for a new unique id', () => {
    const { editor } = setup()
    editor.startEdit(CONFIG_1)
    expect(editor.uniqueCameraId('cam_1')('cam_2')).toBe(true)
  })

  it('returns an error when the id already exists in another camera', () => {
    const cfg = {
      ...CONFIG_1,
      camera_configs: {
        cam_1: { camera_id: 'cam_1', camera_type: 'http', service_url: '' },
        cam_2: { camera_id: 'cam_2', camera_type: 'http', service_url: '' },
      },
    }
    const { editor } = setup()
    editor.startEdit(cfg)
    expect(editor.uniqueCameraId('cam_1')('cam_2')).not.toBe(true)
  })

  it('returns true when the value matches the current id (same-slot edit)', () => {
    const { editor } = setup()
    editor.startEdit(CONFIG_1)
    expect(editor.uniqueCameraId('cam_1')('cam_1')).toBe(true)
  })
})

describe('uniqueStepId', () => {
  it('returns true for a new unique step id', () => {
    const { editor } = setup()
    editor.startEdit(CONFIG_1)
    expect(editor.uniqueStepId('step_1')('step_2')).toBe(true)
  })

  it('returns an error when step id already exists', () => {
    const cfg = {
      ...CONFIG_1,
      pipeline_steps: {
        step_1: CONFIG_1.pipeline_steps.step_1,
        step_2: { camera_id: 'cam_1', model_forwarder_config: { model_name: '', model_serving_url: '' } },
      },
    }
    const { editor } = setup()
    editor.startEdit(cfg)
    expect(editor.uniqueStepId('step_1')('step_2')).not.toBe(true)
  })
})

// ─── onStorageTypeChange ─────────────────────────────────────────────────────

describe('onStorageTypeChange', () => {
  it('sets the storage_type on the config object', () => {
    const { editor } = setup()
    const storage: any = { storage_type: 'filesystem', target_directory: 'data', bucket_name: null }
    editor.onStorageTypeChange(storage, 'gcs')
    expect(storage.storage_type).toBe('gcs')
  })

  it('sets bucket_name to null when switching to filesystem', () => {
    const { editor } = setup()
    const storage: any = { storage_type: 'gcs', target_directory: 'data', bucket_name: 'my-bucket' }
    editor.onStorageTypeChange(storage, 'filesystem')
    expect(storage.bucket_name).toBeNull()
  })

  it('initializes bucket_name to empty string when switching away from filesystem', () => {
    const { editor } = setup()
    const storage: any = { storage_type: 'filesystem', target_directory: 'data', bucket_name: null }
    editor.onStorageTypeChange(storage, 'gcs')
    expect(storage.bucket_name).toBe('')
  })

  it('preserves existing bucket_name when switching to a non-filesystem type', () => {
    const { editor } = setup()
    const storage: any = { storage_type: 'gcs', target_directory: 'data', bucket_name: 'existing' }
    editor.onStorageTypeChange(storage, 's3')
    expect(storage.bucket_name).toBe('existing')
  })
})

// ─── setItemRuleType ─────────────────────────────────────────────────────────

describe('setItemRuleType', () => {
  it('sets item_rule_config to null when type is none', () => {
    const { editor } = setup()
    editor.startEdit({ ...CONFIG_1, item_rule_config: { item_rule_type: 'min_threshold_rule', expected_decision: 'OK', threshold: 1 } })
    editor.setItemRuleType('none')
    expect(editor.draft.value.item_rule_config).toBeNull()
  })

  it('creates a default rule object for a valid type', () => {
    const { editor } = setup()
    editor.startEdit({ ...CONFIG_1, item_rule_config: null })
    editor.setItemRuleType('min_threshold_rule')
    expect(editor.draft.value.item_rule_config).toEqual({
      item_rule_type: 'min_threshold_rule',
      expected_decision: 'OK',
      threshold: 1,
    })
  })
})

// ─── addCamera / removeCamera / renameCameraId ───────────────────────────────

describe('addCamera', () => {
  it('appends a new camera entry to camera_configs', () => {
    const { editor } = setup()
    editor.startEdit(CONFIG_1)
    const before = Object.keys(editor.draft.value.camera_configs).length
    editor.addCamera()
    expect(Object.keys(editor.draft.value.camera_configs).length).toBe(before + 1)
  })
})

describe('removeCamera', () => {
  it('removes the camera from camera_configs', () => {
    const { editor } = setup()
    editor.startEdit(CONFIG_1)
    editor.removeCamera('cam_1')
    expect(editor.draft.value.camera_configs).not.toHaveProperty('cam_1')
  })
})

describe('renameCameraId', () => {
  it('renames the key in camera_configs', () => {
    const { editor } = setup()
    editor.startEdit(CONFIG_1)
    editor.renameCameraId('cam_1', 'cam_renamed')
    expect(editor.draft.value.camera_configs).toHaveProperty('cam_renamed')
    expect(editor.draft.value.camera_configs).not.toHaveProperty('cam_1')
  })

  it('updates the camera_id field inside the entry', () => {
    const { editor } = setup()
    editor.startEdit(CONFIG_1)
    editor.renameCameraId('cam_1', 'cam_renamed')
    expect(editor.draft.value.camera_configs.cam_renamed.camera_id).toBe('cam_renamed')
  })

  it('updates pipeline_steps that referenced the old camera id', () => {
    const { editor } = setup()
    editor.startEdit(CONFIG_1)
    editor.renameCameraId('cam_1', 'cam_renamed')
    expect(editor.draft.value.pipeline_steps.step_1.camera_id).toBe('cam_renamed')
  })

  it('is a no-op when old and new id are identical', () => {
    const { editor } = setup()
    editor.startEdit(CONFIG_1)
    const before = JSON.stringify(editor.draft.value)
    editor.renameCameraId('cam_1', 'cam_1')
    expect(JSON.stringify(editor.draft.value)).toBe(before)
  })
})

// ─── addStep / removeStep / renameStepId ─────────────────────────────────────

describe('addStep', () => {
  it('appends a new step to pipeline_steps', () => {
    const { editor } = setup()
    editor.startEdit(CONFIG_1)
    const before = Object.keys(editor.draft.value.pipeline_steps).length
    editor.addStep()
    expect(Object.keys(editor.draft.value.pipeline_steps).length).toBe(before + 1)
  })
})

describe('removeStep', () => {
  it('removes the step from pipeline_steps', () => {
    const { editor } = setup()
    editor.startEdit(CONFIG_1)
    editor.removeStep('step_1')
    expect(editor.draft.value.pipeline_steps).not.toHaveProperty('step_1')
  })
})

describe('renameStepId', () => {
  it('renames the step key in pipeline_steps', () => {
    const { editor } = setup()
    editor.startEdit(CONFIG_1)
    editor.renameStepId('step_1', 'step_renamed')
    expect(editor.draft.value.pipeline_steps).toHaveProperty('step_renamed')
    expect(editor.draft.value.pipeline_steps).not.toHaveProperty('step_1')
  })

  it('is a no-op when old and new id are identical', () => {
    const { editor } = setup()
    editor.startEdit(CONFIG_1)
    const before = JSON.stringify(editor.draft.value.pipeline_steps)
    editor.renameStepId('step_1', 'step_1')
    expect(JSON.stringify(editor.draft.value.pipeline_steps)).toBe(before)
  })
})

// ─── startEdit / closeDraft / resetDraft ─────────────────────────────────────

describe('startEdit', () => {
  it('sets mode to edit', () => {
    const { editor } = setup()
    editor.startEdit(CONFIG_1)
    expect(editor.mode.value).toBe('edit')
  })

  it('deep-clones the config into draft (mutations do not affect original)', () => {
    const { editor } = setup()
    editor.startEdit(CONFIG_1)
    editor.draft.value.station_name = 'mutated'
    expect(editor.originalConfig.value?.station_name).toBe('config_1')
  })

  it('sets isNewConfig to false', () => {
    const { editor } = setup()
    editor.startEdit(CONFIG_1)
    expect(editor.isNewConfig.value).toBe(false)
  })
})

describe('closeDraft', () => {
  it('resets mode to list', () => {
    const { editor } = setup()
    editor.startEdit(CONFIG_1)
    editor.closeDraft()
    expect(editor.mode.value).toBe('list')
  })

  it('clears draft and originalConfig', () => {
    const { editor } = setup()
    editor.startEdit(CONFIG_1)
    editor.closeDraft()
    expect(editor.draft.value).toBeNull()
    expect(editor.originalConfig.value).toBeNull()
  })
})

describe('resetDraft', () => {
  it('restores draft to the original config values', () => {
    const { editor } = setup()
    editor.startEdit(CONFIG_1)
    editor.draft.value.station_name = 'mutated'
    editor.resetDraft()
    expect(editor.draft.value.station_name).toBe('config_1')
  })

  it('marks isDirty as false after reset', () => {
    const { editor } = setup()
    editor.startEdit(CONFIG_1)
    editor.draft.value.station_name = 'mutated'
    editor.resetDraft()
    expect(editor.isDirty.value).toBe(false)
  })
})

// ─── createNewConfig ──────────────────────────────────────────────────────────

describe('createNewConfig', () => {
  it('sets mode to edit and isNewConfig to true', () => {
    const ctx = makeContext()
    ctx.configs = ref([])
    const editor = useConfigEditor(ctx as any)
    editor.newConfigName.value = 'my_station'
    editor.createNewConfig()
    expect(editor.mode.value).toBe('edit')
    expect(editor.isNewConfig.value).toBe(true)
  })

  it('uses the provided name as station_name', () => {
    const ctx = makeContext()
    ctx.configs = ref([])
    const editor = useConfigEditor(ctx as any)
    editor.newConfigName.value = 'my_station'
    editor.createNewConfig()
    expect(editor.draft.value?.station_name).toBe('my_station')
  })

  it('initializes draft with a default camera entry', () => {
    const ctx = makeContext()
    ctx.configs = ref([])
    const editor = useConfigEditor(ctx as any)
    editor.newConfigName.value = 'my_station'
    editor.createNewConfig()
    expect(Object.keys(editor.draft.value?.camera_configs ?? {}).length).toBeGreaterThan(0)
  })
})

// ─── Async: activateConfig ────────────────────────────────────────────────────

describe('activateConfig', () => {
  it('calls configRepository.activateConfig with the station name', async () => {
    const { editor } = setup()
    await editor.activateConfig('config_1')
    expect(configRepository.activateConfig).toHaveBeenCalledWith('config_1')
  })

  it('shows a success snack on success', async () => {
    const { editor } = setup()
    await editor.activateConfig('config_1')
    expect(editor.snack.value.show).toBe(true)
    expect(editor.snack.value.color).toBe('success')
  })

  it('shows an error snack when the repository rejects', async () => {
    ;(configRepository.activateConfig as ReturnType<typeof vi.fn>).mockRejectedValueOnce(
      { response: { data: { detail: 'not found' } } },
    )
    const { editor } = setup()
    await editor.activateConfig('config_1')
    expect(editor.snack.value.color).toBe('error')
  })

  it('clears activating state after completion', async () => {
    const { editor } = setup()
    await editor.activateConfig('config_1')
    expect(editor.activating.value).toBeNull()
  })
})

// ─── Async: deleteConfig ──────────────────────────────────────────────────────

describe('deleteConfig', () => {
  it('confirmDelete opens the dialog and records the config', () => {
    const { editor } = setup()
    editor.confirmDelete(CONFIG_1)
    expect(editor.deleteConfigDialog.value).toBe(true)
    expect(editor.configToDelete.value).toStrictEqual(CONFIG_1)
  })

  it('calls configRepository.deleteConfig with the station name', async () => {
    const { editor, ctx } = setup()
    editor.confirmDelete(CONFIG_1)
    await editor.deleteConfig()
    expect(configRepository.deleteConfig).toHaveBeenCalledWith('config_1')
  })

  it('calls invalidateConfigs on success', async () => {
    const { editor, ctx } = setup()
    editor.confirmDelete(CONFIG_1)
    await editor.deleteConfig()
    expect(ctx.invalidateConfigs).toHaveBeenCalled()
  })

  it('shows an error snack when the repository rejects', async () => {
    ;(configRepository.deleteConfig as ReturnType<typeof vi.fn>).mockRejectedValueOnce(
      { response: { data: { detail: 'locked' } } },
    )
    const { editor } = setup()
    editor.confirmDelete(CONFIG_1)
    await editor.deleteConfig()
    expect(editor.snack.value.color).toBe('error')
  })
})
