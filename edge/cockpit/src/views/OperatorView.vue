<template>
  <v-container fluid>
    <v-row>
      <!-- Trigger -->
      <v-col cols="12">
        <v-btn
          color="primary"
          size="large"
          prepend-icon="mdi-play"
          :loading="triggering"
          @click="trigger"
        >
          Trigger Inspection
        </v-btn>
      </v-col>

      <!-- Results table -->
      <v-col cols="12">
        <v-card>
          <v-card-title>Recent Inspections</v-card-title>
          <v-data-table
            :headers="headers"
            :items="items"
            :loading="loading"
            density="compact"
          >
            <template #item.decision="{ item }">
              <v-chip :color="item.decision === 'OK' ? 'success' : 'error'" size="small" label>
                {{ item.decision }}
              </v-chip>
            </template>
          </v-data-table>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api'

const items = ref([])
const loading = ref(false)
const triggering = ref(false)

const headers = [
  { title: 'Item ID', key: 'id' },
  { title: 'Timestamp', key: 'created_at' },
  { title: 'Decision', key: 'decision' },
  { title: 'Camera', key: 'camera_id' },
]

async function loadItems() {
  loading.value = true
  try {
    const res = await api.getItems()
    items.value = res.data
  } finally {
    loading.value = false
  }
}

async function trigger() {
  triggering.value = true
  try {
    await api.trigger()
    await loadItems()
  } finally {
    triggering.value = false
  }
}

onMounted(loadItems)
</script>
