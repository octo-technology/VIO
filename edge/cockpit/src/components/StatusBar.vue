<template>
  <v-app-bar elevation="1">
    <v-app-bar-title>VIO Cockpit</v-app-bar-title>
    <template #append>
      <v-chip
        :color="orchestratorOk ? 'success' : 'error'"
        class="mr-2"
        size="small"
        label
        clickable
        @click="openDetail('orchestrator')"
      >
        <v-icon start>{{ orchestratorOk ? 'mdi-check-circle' : 'mdi-alert-circle' }}</v-icon>
        Orchestrator
      </v-chip>

      <v-chip
        v-if="cameraService"
        :color="cameraService.ok ? 'success' : 'error'"
        class="mr-2"
        size="small"
        label
        clickable
        @click="openDetail('camera')"
      >
        <v-icon start>{{ cameraService.ok ? 'mdi-check-circle' : 'mdi-alert-circle' }}</v-icon>
        Camera
      </v-chip>

      <v-chip
        v-if="modelService"
        :color="modelService.ok ? 'success' : 'error'"
        class="mr-2"
        size="small"
        label
        clickable
        @click="openDetail('model')"
      >
        <v-icon start>{{ modelService.ok ? 'mdi-check-circle' : 'mdi-alert-circle' }}</v-icon>
        Model Server
      </v-chip>
    </template>
  </v-app-bar>

  <v-dialog v-model="dialog" max-width="440">
    <v-card v-if="selectedService === 'orchestrator'">
      <v-card-title class="text-subtitle-1 font-weight-bold pt-4 px-4">Orchestrator</v-card-title>
      <v-card-text class="px-2 pb-2">
        <v-list density="compact">
          <v-list-item>
            <template #prepend>
              <v-icon :color="orchestratorOk ? 'success' : 'error'" class="mr-2">
                {{ orchestratorOk ? 'mdi-check-circle' : 'mdi-alert-circle' }}
              </v-icon>
            </template>
            <v-list-item-title>Liveness</v-list-item-title>
            <template #append>
              <v-chip :color="orchestratorOk ? 'success' : 'error'" size="x-small" label>
                {{ orchestratorOk ? 'ok' : 'down' }}
              </v-chip>
            </template>
          </v-list-item>
          <v-list-item>
            <template #prepend>
              <v-icon class="mr-2">mdi-cog</v-icon>
            </template>
            <v-list-item-title>Active config</v-list-item-title>
            <template #append>
              <span class="text-caption text-medium-emphasis">{{ activeConfigName || '—' }}</span>
            </template>
          </v-list-item>
        </v-list>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn variant="text" @click="dialog = false">Close</v-btn>
      </v-card-actions>
    </v-card>

    <v-card v-else-if="selectedService === 'camera'">
      <v-card-title class="text-subtitle-1 font-weight-bold pt-4 px-4">Camera Service</v-card-title>
      <v-card-text class="px-2 pb-2">
        <v-list density="compact">
          <template v-for="(cameras, url) in dialogCameras" :key="url">
            <v-list-subheader>{{ url }}</v-list-subheader>
            <v-list-item v-for="(info, id) in cameras" :key="id">
              <template #prepend>
                <v-icon color="success" class="mr-2">mdi-camera</v-icon>
              </template>
              <v-list-item-title>{{ id }}</v-list-item-title>
              <v-list-item-subtitle v-if="info.backend">{{ info.backend }}</v-list-item-subtitle>
            </v-list-item>
          </template>
          <v-list-item v-if="Object.keys(dialogCameras).length === 0">
            <template #prepend>
              <v-icon :color="cameraService?.ok ? 'success' : 'error'" class="mr-2">
                {{ cameraService?.ok ? 'mdi-check-circle' : 'mdi-alert-circle' }}
              </v-icon>
            </template>
            <v-list-item-title>{{ cameraService?.ok ? 'Service up — no cameras found' : 'Service unreachable' }}</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn variant="text" @click="dialog = false">Close</v-btn>
      </v-card-actions>
    </v-card>

    <v-card v-else-if="selectedService === 'model'">
      <v-card-title class="text-subtitle-1 font-weight-bold pt-4 px-4">Model Server</v-card-title>
      <v-card-text class="px-2 pb-2">
        <v-list density="compact">
          <template v-for="(modelNames, url) in dialogModels" :key="url">
            <v-list-subheader>{{ url }}</v-list-subheader>
            <v-list-item v-for="name in modelNames" :key="name">
              <template #prepend>
                <v-icon color="success" class="mr-2">mdi-brain</v-icon>
              </template>
              <v-list-item-title>{{ name }}</v-list-item-title>
              <v-list-item-subtitle>tflite</v-list-item-subtitle>
            </v-list-item>
          </template>
          <v-list-item v-if="Object.keys(dialogModels).length === 0">
            <template #prepend>
              <v-icon :color="modelService?.ok ? 'success' : 'error'" class="mr-2">
                {{ modelService?.ok ? 'mdi-check-circle' : 'mdi-alert-circle' }}
              </v-icon>
            </template>
            <v-list-item-title>{{ modelService?.ok ? 'Service up — no models found' : 'Service unreachable' }}</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn variant="text" @click="dialog = false">Close</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref } from 'vue'
import { storeToRefs } from 'pinia'
import { useHealthStore } from '../features/system-health/stores/healthStore'
import * as discoveryRepository from '../features/station-config/api/discoveryRepository'

const healthStore = useHealthStore()
const { orchestratorOk, cameraService, modelService, activeConfigName } = storeToRefs(healthStore)

const dialog = ref(false)
const selectedService = ref(null)
const dialogCameras = ref({})
const dialogModels = ref({})

async function openDetail(service) {
  selectedService.value = service
  dialog.value = true
  if (service === 'camera') {
    const result = await discoveryRepository.getCamerasAvailable().catch(() => null)
    dialogCameras.value = result?.cameras ?? {}
  } else if (service === 'model') {
    const result = await discoveryRepository.getModelsAvailable().catch(() => null)
    dialogModels.value = result?.models ?? {}
  }
}
</script>
