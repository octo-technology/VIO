<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12" md="4">
        <v-card>
          <v-card-title>Active Configuration</v-card-title>
          <v-card-text>
            <v-select
              v-model="selectedConfig"
              :items="configs"
              item-title="station_name"
              item-value="station_name"
              label="Station config"
              :loading="loading"
            />
          </v-card-text>
          <v-card-actions>
            <v-btn color="primary" :disabled="!selectedConfig" @click="applyConfig">
              Apply
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
      <v-col cols="12" md="8">
        <v-card>
          <v-card-title>Configuration Preview</v-card-title>
          <v-card-text>
            <pre v-if="selectedConfigDetail" class="config-preview">{{ JSON.stringify(selectedConfigDetail, null, 2) }}</pre>
            <v-empty-state v-else icon="mdi-cog-outline" title="Select a configuration to preview" />
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import api from '../services/api'

const configs = ref([])
const selectedConfig = ref(null)
const selectedConfigDetail = ref(null)
const loading = ref(false)

async function loadConfigs() {
  loading.value = true
  try {
    const [configsRes, activeRes] = await Promise.all([api.getConfigs(), api.getActiveConfig()])
    configs.value = configsRes.data
    selectedConfig.value = activeRes.data?.station_name ?? null
  } finally {
    loading.value = false
  }
}

watch(selectedConfig, (name) => {
  selectedConfigDetail.value = configs.value.find((c) => c.station_name === name) ?? null
})

async function applyConfig() {
  await api.setActiveConfig(selectedConfig.value)
}

onMounted(loadConfigs)
</script>

<style scoped>
.config-preview {
  font-size: 12px;
  white-space: pre-wrap;
  word-break: break-word;
}
</style>
