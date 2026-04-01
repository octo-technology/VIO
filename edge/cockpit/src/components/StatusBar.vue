<template>
  <v-app-bar elevation="1">
    <v-app-bar-title>VIO Cockpit</v-app-bar-title>
    <template #append>
      <v-chip
        :color="orchestratorOk ? 'success' : 'error'"
        class="mr-2"
        size="small"
        label
      >
        <v-icon start>{{ orchestratorOk ? 'mdi-check-circle' : 'mdi-alert-circle' }}</v-icon>
        Orchestrator
      </v-chip>
      <v-chip
        v-for="svc in downstreamServices"
        :key="svc.name"
        :color="svc.ok ? 'success' : 'error'"
        class="mr-2"
        size="small"
        label
      >
        <v-icon start>{{ svc.ok ? 'mdi-check-circle' : 'mdi-alert-circle' }}</v-icon>
        {{ svc.name }}
      </v-chip>
      <v-chip class="mr-2" size="small" label>
        <v-icon start>mdi-cog</v-icon>
        {{ activeConfig || '—' }}
      </v-chip>
    </template>
  </v-app-bar>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import api from '../services/api'

const activeConfig = ref(null)
const orchestratorOk = ref(false)
const downstreamServices = ref([])

async function poll() {
  const [liveRes, servicesRes, configRes] = await Promise.allSettled([
    api.getHealth(),
    api.getServicesHealth(),
    api.getActiveConfig(),
  ])

  orchestratorOk.value = liveRes.status === 'fulfilled'

  if (servicesRes.status === 'fulfilled') {
    const entries = Object.entries(servicesRes.value.data.services)
    downstreamServices.value = entries.map(([url, ok]) => ({
      name: serviceLabel(url),
      ok,
    }))
  }

  if (configRes.status === 'fulfilled') {
    activeConfig.value = configRes.value.data?.station_name ?? null
  }
}

function serviceLabel(url) {
  if (url.includes('8001')) return 'Camera'
  if (url.includes('8501')) return 'Model Server'
  return url
}

let timer
onMounted(() => { poll(); timer = setInterval(poll, 5000) })
onUnmounted(() => clearInterval(timer))
</script>
