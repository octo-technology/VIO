<template>
  <v-container fluid>
    <!-- LIST MODE -->
    <template v-if="mode === 'list'">
      <v-col v-if="!stationConfig" cols="12" class="pa-0 mb-4">
        <v-alert type="warning" variant="tonal" icon="mdi-alert-circle-outline">
          Aucune configuration active. Rendez-vous dans
          <router-link :to="{ name: 'technician' }" class="text-warning font-weight-bold">Configuration</router-link>
          pour en sélectionner ou en créer une.
        </v-alert>
      </v-col>

      <div class="d-flex align-center gap-3 mb-4">
        <v-btn
          color="primary"
          size="large"
          prepend-icon="mdi-play"
          :loading="triggering"
          :disabled="!stationConfig"
          @click="trigger"
        >
          Trigger Inspection
        </v-btn>
      </div>

      <v-card>
        <v-card-title>Recent Inspections</v-card-title>
        <v-data-table
          :headers="headers"
          :items="items"
          :loading="loading"
          density="compact"
          hover
          @click:row="onRowClick"
        >
          <template #item.decision="{ item }">
            <ItemDecisionChip :item="item" />
          </template>
        </v-data-table>
      </v-card>
    </template>

    <!-- DETAIL MODE -->
    <template v-else>
      <InspectionDetail
        :item="selectedItem"
        :station-config="stationConfig"
        :polling="polling"
        :loading-detail="loadingDetail"
        :item-image-url="itemImageUrl"
        @back="mode = 'list'"
        @open-lightbox="openLightbox"
      />
    </template>

    <LightboxDialog
      v-model="lightboxOpen"
      :img-src="lightboxImgSrc"
      :predictions="lightboxPredictions"
    />

    <v-snackbar v-model="snack.show" :color="snack.color" timeout="4000" location="bottom right">
      {{ snack.message }}
    </v-snackbar>
  </v-container>
</template>

<script setup>
import { ref, computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useHealthStore } from '../features/system-health/stores/healthStore'
import { useItems } from '../features/inspection/composables/useItems'
import { useTrigger } from '../features/inspection/composables/useTrigger'
import ItemDecisionChip from '../features/inspection/components/ItemDecisionChip.vue'
import InspectionDetail from '../features/inspection/components/InspectionDetail.vue'
import LightboxDialog from '../features/inspection/components/LightboxDialog.vue'

const { activeConfig: stationConfig } = storeToRefs(useHealthStore())
const hasConfig = computed(() => !!stationConfig.value)
const { items, isLoading: loading, fetchItem, itemImageUrl } = useItems({ enabled: hasConfig })
const { triggering, polling, triggerInspection } = useTrigger()

const mode = ref('list')
const selectedItem = ref(null)
const loadingDetail = ref(false)
const lightboxOpen = ref(false)
const lightboxCameraId = ref(null)
const snack = ref({ show: false, message: '', color: 'error' })

const headers = [
  { title: 'Item ID', key: 'id' },
  { title: 'Created', key: 'creation_date' },
  { title: 'Decision', key: 'decision' },
  { title: 'State', key: 'state' },
]

const lightboxImgSrc = computed(() =>
  selectedItem.value && lightboxCameraId.value
    ? itemImageUrl(selectedItem.value.id, lightboxCameraId.value)
    : ''
)

const lightboxPredictions = computed(() => predictionsForCamera(lightboxCameraId.value))

function openDetail(item) {
  selectedItem.value = {
    id: item.id,
    creation_date: item.creation_date,
    decision: item.decision,
    state: item.state,
    cameras_metadata: {},
    predictions: {},
  }
  mode.value = 'detail'
  loadingDetail.value = true
  fetchItem(item.id)
    .then(data => { selectedItem.value = data })
    .finally(() => { loadingDetail.value = false })
}

function onRowClick(_event, { item }) {
  openDetail(item)
}

function openLightbox(cameraId) {
  lightboxCameraId.value = cameraId
  lightboxOpen.value = true
}

async function trigger() {
  try {
    await triggerInspection({
      onPending: (itemId) => {
        selectedItem.value = { id: itemId, state: 'PENDING', cameras_metadata: {}, predictions: {} }
        mode.value = 'detail'
      },
      onUpdate: (item) => { selectedItem.value = item },
    })
  } catch (e) {
    const detail = e?.response?.data?.detail
    snack.value = { show: true, message: detail ?? 'Trigger failed', color: 'error' }
  }
}

// --- Helpers ---

function predictionsForCamera(cameraId) {
  if (!selectedItem.value || !stationConfig.value || !cameraId) return []
  return Object.entries(stationConfig.value.pipeline_steps || {})
    .filter(([, step]) => step.camera_id === cameraId)
    .map(([stepId, step]) => ({ stepId, step, pred: selectedItem.value.predictions?.[stepId] ?? null }))
    .filter(({ pred }) => pred !== null)
}
</script>
