<template>
  <div class="text-subtitle-1 mb-2">Cameras</div>
  <v-table density="compact" class="mb-1">
    <thead>
      <tr>
        <th>ID</th>
        <th>Service URL</th>
        <th class="text-medium-emphasis">Backend</th>
        <th class="text-medium-emphasis">Position</th>
        <th />
      </tr>
    </thead>
    <tbody>
      <tr v-for="(cam, camId) in cameraConfigs" :key="camId">
        <td style="width:160px">
          <v-combobox
            :model-value="camId"
            :items="camerasForUrl(cam.service_url)"
            :rules="[rules.required, uniqueCameraId(camId)]"
            density="compact"
            variant="underlined"
            hide-details="auto"
            hide-no-data
            @update:model-value="(v) => $emit('rename-camera', camId, v)"
          />
        </td>
        <td>
          <v-select
            v-model="cam.service_url"
            :items="cameraServiceUrls"
            :rules="[rules.required]"
            density="compact"
            variant="underlined"
            hide-details="auto"
          />
        </td>
        <td style="width:100px" class="text-caption text-medium-emphasis">
          {{ cameraBackendForUrl(cam.service_url, camId)?.backend || '—' }}
        </td>
        <td style="width:100px" class="text-caption text-medium-emphasis">
          {{ cameraBackendForUrl(cam.service_url, camId)?.position || '—' }}
        </td>
        <td style="width:40px">
          <v-btn
            icon="mdi-delete-outline"
            size="x-small"
            variant="text"
            color="error"
            :disabled="Object.keys(cameraConfigs).length <= 1"
            @click="$emit('remove-camera', camId)"
          />
        </td>
      </tr>
    </tbody>
  </v-table>
  <div class="d-flex justify-end mb-4">
    <v-btn size="x-small" variant="tonal" prepend-icon="mdi-plus" @click="$emit('add-camera')">Add camera</v-btn>
  </div>
</template>

<script setup>
defineProps({
  cameraConfigs: { type: Object, required: true },
  cameraServiceUrls: { type: Array, required: true },
  camerasForUrl: { type: Function, required: true },
  cameraBackendForUrl: { type: Function, required: true },
  rules: { type: Object, required: true },
  uniqueCameraId: { type: Function, required: true },
})

defineEmits(['rename-camera', 'remove-camera', 'add-camera'])
</script>
