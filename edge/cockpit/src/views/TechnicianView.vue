<template>
  <v-container fluid>
    <v-row>
      <!-- Config selector -->
      <v-col cols="12" md="3">
        <v-card>
          <v-card-title>Configurations</v-card-title>
          <v-card-text>
            <v-list density="compact" nav>
              <v-list-item
                v-for="cfg in configs"
                :key="cfg.station_name"
                :value="cfg.station_name"
                :active="selectedConfig === cfg.station_name"
                color="primary"
                rounded="lg"
                @click="selectConfig(cfg.station_name)"
              >
                <v-list-item-title>{{ cfg.station_name }}</v-list-item-title>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Config editor -->
      <v-col v-if="draft" cols="12" md="9">
        <v-card>
          <v-card-title class="d-flex align-center gap-2">
            {{ draft.station_name }}
            <v-spacer />
            <v-btn variant="outlined" size="small" @click="resetDraft">Reset</v-btn>
            <v-btn color="primary" size="small" :loading="saving" @click="applyConfig">Apply</v-btn>
          </v-card-title>

          <v-card-text>
            <!-- Cameras -->
            <div class="d-flex align-center mb-2">
              <span class="text-subtitle-1">Cameras</span>
              <v-spacer />
              <v-btn size="x-small" variant="tonal" prepend-icon="mdi-plus" @click="addCamera">Add camera</v-btn>
            </div>
            <v-table density="compact" class="mb-4">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Type</th>
                  <th>Service URL</th>
                  <th>Position</th>
                  <th />
                </tr>
              </thead>
              <tbody>
                <tr v-for="(cam, camId) in draft.camera_configs" :key="camId">
                  <td style="width:160px">
                    <v-text-field
                      :model-value="camId"
                      density="compact"
                      variant="underlined"
                      hide-details
                      @update:model-value="(v) => renameCameraId(camId, v)"
                    />
                  </td>
                  <td style="width:120px">
                    <v-select
                      v-model="cam.camera_type"
                      :items="['http']"
                      density="compact"
                      variant="underlined"
                      hide-details
                    />
                  </td>
                  <td>
                    <v-text-field
                      v-model="cam.service_url"
                      density="compact"
                      variant="underlined"
                      hide-details
                    />
                  </td>
                  <td style="width:120px">
                    <v-text-field
                      v-model="cam.position"
                      density="compact"
                      variant="underlined"
                      hide-details
                    />
                  </td>
                  <td style="width:40px">
                    <v-btn
                      icon="mdi-delete-outline"
                      size="x-small"
                      variant="text"
                      color="error"
                      :disabled="Object.keys(draft.camera_configs).length <= 1"
                      @click="removeCamera(camId)"
                    />
                  </td>
                </tr>
              </tbody>
            </v-table>

            <!-- Pipeline steps -->
            <div class="d-flex align-center mb-2">
              <span class="text-subtitle-1">Pipeline steps</span>
              <v-spacer />
              <v-btn size="x-small" variant="tonal" prepend-icon="mdi-plus" @click="addStep">Add step</v-btn>
            </div>
            <v-table density="compact" class="mb-4">
              <thead>
                <tr>
                  <th>Step</th>
                  <th>Camera</th>
                  <th>Model</th>
                  <th>Version</th>
                  <th>Model server URL</th>
                  <th />
                </tr>
              </thead>
              <tbody>
                <tr v-for="(step, stepId) in draft.pipeline_steps" :key="stepId">
                  <td style="width:130px">
                    <v-text-field
                      :model-value="stepId"
                      density="compact"
                      variant="underlined"
                      hide-details
                      @update:model-value="(v) => renameStepId(stepId, v)"
                    />
                  </td>
                  <td style="width:140px">
                    <v-select
                      v-model="step.camera_id"
                      :items="Object.keys(draft.camera_configs)"
                      density="compact"
                      variant="underlined"
                      hide-details
                    />
                  </td>
                  <td>
                    <v-text-field
                      v-model="step.model_forwarder_config.model_name"
                      density="compact"
                      variant="underlined"
                      hide-details
                    />
                  </td>
                  <td style="width:80px">
                    <v-text-field
                      v-model="step.model_forwarder_config.model_version"
                      density="compact"
                      variant="underlined"
                      hide-details
                    />
                  </td>
                  <td>
                    <v-text-field
                      v-model="step.model_forwarder_config.model_serving_url"
                      density="compact"
                      variant="underlined"
                      hide-details
                    />
                  </td>
                  <td style="width:40px">
                    <v-btn
                      icon="mdi-delete-outline"
                      size="x-small"
                      variant="text"
                      color="error"
                      :disabled="Object.keys(draft.pipeline_steps).length <= 1"
                      @click="removeStep(stepId)"
                    />
                  </td>
                </tr>
              </tbody>
            </v-table>

            <!-- Storage -->
            <div class="text-subtitle-1 mb-2">Storage</div>
            <v-row>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="draft.binary_storage_config.target_directory"
                  label="Binary storage path"
                  density="compact"
                  variant="outlined"
                  hide-details
                />
              </v-col>
              <v-col cols="12" sm="6">
                <v-text-field
                  v-model="draft.metadata_storage_config.target_directory"
                  label="Metadata storage path"
                  density="compact"
                  variant="outlined"
                  hide-details
                />
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col v-else cols="12" md="9">
        <v-empty-state icon="mdi-cog-outline" title="Select a configuration to edit" />
      </v-col>
    </v-row>

    <v-snackbar v-model="snack.show" :color="snack.color" timeout="3000" location="bottom right">
      {{ snack.message }}
    </v-snackbar>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api'

const configs = ref([])
const selectedConfig = ref(null)
const draft = ref(null)
const originalConfig = ref(null)
const loading = ref(false)
const saving = ref(false)
const snack = ref({ show: false, message: '', color: 'success' })

function notify(message, color = 'success') {
  snack.value = { show: true, message, color }
}

async function loadConfigs() {
  loading.value = true
  try {
    const [configsRes, activeRes] = await Promise.all([api.getConfigs(), api.getActiveConfig()])
    configs.value = Object.values(configsRes.data)
    const activeName = activeRes.data?.station_name ?? null
    if (activeName) selectConfig(activeName)
  } finally {
    loading.value = false
  }
}

function selectConfig(name) {
  selectedConfig.value = name
  const cfg = configs.value.find((c) => c.station_name === name)
  if (cfg) {
    originalConfig.value = cfg
    draft.value = JSON.parse(JSON.stringify(cfg))
  }
}

function resetDraft() {
  if (originalConfig.value) {
    draft.value = JSON.parse(JSON.stringify(originalConfig.value))
  }
}

async function applyConfig() {
  saving.value = true
  try {
    await api.setActiveConfig(draft.value)
    originalConfig.value = JSON.parse(JSON.stringify(draft.value))
    await loadConfigs()
    notify(`Config "${draft.value.station_name}" applied successfully`)
  } catch (e) {
    notify(e?.response?.data?.detail ?? 'Failed to apply config', 'error')
  } finally {
    saving.value = false
  }
}

function addStep() {
  const newId = `step_${Object.keys(draft.value.pipeline_steps).length + 1}`
  const firstCamera = Object.keys(draft.value.camera_configs)[0] ?? ''
  draft.value.pipeline_steps = {
    ...draft.value.pipeline_steps,
    [newId]: {
      camera_id: firstCamera,
      model_forwarder_config: { model_name: '', model_version: '1', model_serving_url: '' },
    },
  }
}

function removeStep(stepId) {
  const updated = { ...draft.value.pipeline_steps }
  delete updated[stepId]
  draft.value.pipeline_steps = updated
}

function renameStepId(oldId, newId) {
  if (!newId || newId === oldId) return
  const updated = {}
  for (const [k, v] of Object.entries(draft.value.pipeline_steps)) {
    updated[k === oldId ? newId : k] = v
  }
  draft.value.pipeline_steps = updated
}

function addCamera() {
  const newId = `camera_${Object.keys(draft.value.camera_configs).length + 1}`
  draft.value.camera_configs = {
    ...draft.value.camera_configs,
    [newId]: { camera_id: newId, camera_type: 'http', position: '', service_url: '' },
  }
}

function removeCamera(camId) {
  const updated = { ...draft.value.camera_configs }
  delete updated[camId]
  draft.value.camera_configs = updated
}

function renameCameraId(oldId, newId) {
  if (!newId || newId === oldId) return
  const updated = {}
  for (const [k, v] of Object.entries(draft.value.camera_configs)) {
    updated[k === oldId ? newId : k] = k === oldId ? { ...v, camera_id: newId } : v
  }
  draft.value.camera_configs = updated
  for (const step of Object.values(draft.value.pipeline_steps)) {
    if (step.camera_id === oldId) step.camera_id = newId
  }
}

onMounted(loadConfigs)
</script>
