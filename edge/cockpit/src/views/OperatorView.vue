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

      <!-- Last inspection result -->
      <v-col v-if="lastItem" cols="12">
        <v-card>
          <v-card-title class="d-flex align-center gap-2">
            Last Inspection
            <v-chip :color="lastItem.state === 'DONE' ? (lastItem.decision === 'OK' ? 'success' : 'error') : 'warning'" size="small" label>
              {{ lastItem.state === 'DONE' ? lastItem.decision : lastItem.state }}
            </v-chip>
            <v-progress-circular v-if="polling" indeterminate size="20" class="ml-2" />
          </v-card-title>
          <v-card-subtitle>
            {{ lastItem.id }}
            <span v-if="lastItem.creation_date" class="ml-3 text-medium-emphasis">
              {{ new Date(lastItem.creation_date).toLocaleString() }}
            </span>
          </v-card-subtitle>
          <v-card-text>
            <v-row>
              <v-col
                v-for="(_, cameraId) in lastItem.cameras_metadata"
                :key="cameraId"
                cols="12"
                sm="6"
                md="4"
              >
                <v-card variant="outlined">
                  <v-card-subtitle>{{ cameraId }}</v-card-subtitle>
                  <v-img
                    :src="api.getItemImage(lastItem.id, cameraId)"
                    height="200"
                    cover
                    :lazy-src="null"
                  >
                    <template #error>
                      <v-sheet height="200" class="d-flex align-center justify-center text-medium-emphasis">
                        No image
                      </v-sheet>
                    </template>
                  </v-img>
                </v-card>
              </v-col>
            </v-row>
            <v-row v-if="stationConfig?.pipeline_steps">
              <v-col cols="12">
                <div class="text-subtitle-2 mb-2">Pipeline results</div>
                <v-table density="compact" class="mb-3">
                  <thead>
                    <tr>
                      <th>Step</th>
                      <th>Camera</th>
                      <th>Prediction</th>
                      <th>Camera rule</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(step, stepId) in stationConfig.pipeline_steps" :key="stepId">
                      <td>{{ stepId }}</td>
                      <td>{{ step.camera_id }}</td>
                      <td>{{ predictionText(lastItem.predictions?.[stepId]) }}</td>
                      <td class="text-medium-emphasis">{{ cameraRuleText(step.camera_rule_config) ?? '—' }}</td>
                    </tr>
                  </tbody>
                </v-table>
                <div class="text-subtitle-2 mb-2">Final decision rule</div>
                <v-chip size="small" variant="tonal" prepend-icon="mdi-scale-balance">
                  {{ itemRuleText(stationConfig.item_rule_config) ?? 'No item rule defined' }}
                </v-chip>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
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
            hover
            @click:row="openDetail"
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

    <!-- Detail dialog -->
    <v-dialog v-model="detailOpen" max-width="960" scrollable>
      <v-card>
        <v-card-title class="d-flex align-center gap-2 flex-wrap">
          <span class="text-truncate" style="max-width:520px">{{ selectedItem?.id }}</span>
          <v-chip
            v-if="selectedItem"
            :color="selectedItem.decision === 'OK' ? 'success' : 'error'"
            size="small"
            label
          >
            {{ selectedItem.decision }}
          </v-chip>
          <v-spacer />
          <v-btn icon="mdi-close" variant="text" @click="detailOpen = false" />
        </v-card-title>

        <v-card-subtitle v-if="selectedItem">{{ selectedItem.creation_date }}</v-card-subtitle>

        <v-card-text>
          <v-progress-linear v-if="loadingDetail" indeterminate class="mb-4" />

          <template v-if="selectedItem">
            <!-- Photos -->
            <div class="text-subtitle-2 mb-2">Photos</div>
            <v-row class="mb-4">
              <v-col
                v-for="(_, cameraId) in selectedItem.cameras_metadata"
                :key="cameraId"
                cols="12"
                sm="6"
                md="4"
              >
                <v-card variant="outlined">
                  <v-card-subtitle>{{ cameraId }}</v-card-subtitle>
                  <v-img
                    :src="api.getItemImage(selectedItem.id, cameraId)"
                    height="200"
                    cover
                    :lazy-src="null"
                  >
                    <template #error>
                      <v-sheet height="200" class="d-flex align-center justify-center text-medium-emphasis">
                        No image
                      </v-sheet>
                    </template>
                  </v-img>
                </v-card>
              </v-col>
            </v-row>

            <!-- Pipeline results -->
            <div class="text-subtitle-2 mb-2">Pipeline results</div>
            <v-table density="compact" class="mb-4">
              <thead>
                <tr>
                  <th>Step</th>
                  <th>Camera</th>
                  <th>Prediction</th>
                  <th>Camera rule</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(step, stepId) in stationConfig?.pipeline_steps" :key="stepId">
                  <td>{{ stepId }}</td>
                  <td>{{ step.camera_id }}</td>
                  <td>{{ predictionText(selectedItem.predictions?.[stepId]) }}</td>
                  <td class="text-medium-emphasis">{{ cameraRuleText(step.camera_rule_config) ?? '—' }}</td>
                </tr>
              </tbody>
            </v-table>

            <!-- Item rule -->
            <div class="text-subtitle-2 mb-2">Final decision rule</div>
            <v-chip size="small" variant="tonal" prepend-icon="mdi-scale-balance">
              {{ itemRuleText(stationConfig?.item_rule_config) ?? 'No item rule defined' }}
            </v-chip>
          </template>
        </v-card-text>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '../services/api'

const items = ref([])
const loading = ref(false)
const triggering = ref(false)
const lastItem = ref(null)
const polling = ref(false)
const stationConfig = ref(null)
const selectedItem = ref(null)
const detailOpen = ref(false)
const loadingDetail = ref(false)

const headers = [
  { title: 'Item ID', key: 'id' },
  { title: 'Created', key: 'creation_date' },
  { title: 'Decision', key: 'decision' },
  { title: 'State', key: 'state' },
]

async function loadItems() {
  loading.value = true
  try {
    const [itemsRes, configRes] = await Promise.all([api.getItems(), api.getActiveConfig()])
    items.value = itemsRes.data
    stationConfig.value = configRes.data
  } finally {
    loading.value = false
  }
}

async function openDetail(_event, { item }) {
  selectedItem.value = { id: item.id, creation_date: item.creation_date, decision: item.decision, cameras_metadata: {}, predictions: {} }
  detailOpen.value = true
  loadingDetail.value = true
  try {
    const res = await api.getItem(item.id)
    selectedItem.value = res.data
  } finally {
    loadingDetail.value = false
  }
}

async function pollUntilDone(itemId) {
  polling.value = true
  const deadline = Date.now() + 30_000
  while (Date.now() < deadline) {
    try {
      const res = await api.getItem(itemId)
      lastItem.value = res.data
      if (res.data.state === 'DONE') break
    } catch (_) {
      // item may not be persisted yet — keep polling
    }
    await new Promise((r) => setTimeout(r, 500))
  }
  polling.value = false
  await loadItems()
}

async function trigger() {
  triggering.value = true
  lastItem.value = null
  try {
    const res = await api.trigger()
    const itemId = res.data?.item_id
    if (!itemId) throw new Error('No item_id returned by trigger')
    lastItem.value = { id: itemId, state: 'PENDING', cameras_metadata: {}, predictions: {} }
    await pollUntilDone(itemId)
  } catch (e) {
    console.error('Trigger failed:', e)
  } finally {
    triggering.value = false
  }
}

function cameraRuleText(rule) {
  if (!rule) return null
  switch (rule.camera_rule_type) {
    case 'expected_label_rule':
      return `Expects class "${rule.expected_class}"`
    case 'unexpected_label_rule':
      return `Rejects if class "${rule.unexpected_class}" detected`
    case 'min_nb_objects_rule':
      return `At least ${rule.threshold} "${rule.class_to_detect}" object(s) required`
    case 'max_nb_objects_rule':
      return `At most ${rule.threshold} "${rule.class_to_detect}" object(s) allowed`
    default:
      return rule.camera_rule_type
  }
}

function itemRuleText(rule) {
  if (!rule) return null
  switch (rule.item_rule_type) {
    case 'min_threshold_rule':
      return `At least ${rule.threshold} camera(s) must return "${rule.expected_decision}"`
    case 'min_threshold_ratio_rule':
      return `At least ${(rule.threshold * 100).toFixed(0)}% of cameras must return "${rule.expected_decision}"`
    default:
      return rule.item_rule_type
  }
}

function predictionText(pred) {
  if (!pred) return '—'
  if (pred.prediction_type === 'class') return `${pred.label} (${(pred.probability * 100).toFixed(1)}%)`
  return `${Object.keys(pred.detected_objects || {}).length} object(s)`
}

onMounted(loadItems)
</script>
