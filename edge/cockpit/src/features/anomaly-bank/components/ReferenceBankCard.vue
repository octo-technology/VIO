<template>
  <v-card>
    <v-card-title class="text-h6">Teach reference images</v-card-title>
    <v-card-subtitle>
      Upload anomaly-free ("good") images to extend the model's memory bank. The bank is saved on the
      serving backend, so it survives restarts.
    </v-card-subtitle>

    <v-card-text>
      <v-select
        v-model="selectedModel"
        :items="models"
        label="Model"
        density="comfortable"
        variant="outlined"
        :disabled="uploading"
        hide-details="auto"
        class="mb-4"
      />

      <v-file-input
        v-model="files"
        label="Normal images"
        accept="image/*"
        multiple
        chips
        show-size
        prepend-icon="mdi-image-multiple"
        variant="outlined"
        :disabled="uploading"
        hide-details="auto"
        class="mb-4"
      />

      <v-btn
        color="primary"
        prepend-icon="mdi-brain"
        :loading="uploading"
        :disabled="!canTeach"
        @click="onTeach"
      >
        Teach {{ fileCount ? `(${fileCount})` : '' }}
      </v-btn>

      <div v-if="job" class="mt-6">
        <div class="d-flex align-center mb-1">
          <span class="text-body-2">{{ statusLabel }}</span>
          <v-spacer />
          <span class="text-body-2 text-medium-emphasis">{{ job.processed }} / {{ job.total }}</span>
        </div>
        <v-progress-linear
          :model-value="progress"
          :indeterminate="uploading && job.total === 0"
          :color="progressColor"
          height="8"
          rounded
        />

        <v-alert v-if="job.status === 'completed'" type="success" variant="tonal" class="mt-4" density="comfortable">
          Bank updated — it now holds {{ job.bank_size }} reference image(s).
        </v-alert>
        <v-alert v-else-if="job.status === 'failed'" type="error" variant="tonal" class="mt-4" density="comfortable">
          {{ job.error || 'The fit failed.' }}
        </v-alert>
      </div>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useReferenceBank } from '../composables/useReferenceBank'

const props = defineProps({
  models: { type: Array, default: () => [] },
})

const { uploading, job, progress, teach } = useReferenceBank()

const selectedModel = ref(props.models[0] ?? null)
const files = ref([])

// Default to the first model once the list arrives.
watch(
  () => props.models,
  (models) => {
    if (!selectedModel.value && models.length) selectedModel.value = models[0]
  },
)

const fileCount = computed(() => files.value.length)
const canTeach = computed(() => !!selectedModel.value && fileCount.value > 0 && !uploading.value)

const statusLabel = computed(() => {
  if (!job.value) return ''
  switch (job.value.status) {
    case 'pending':
      return 'Queued…'
    case 'running':
      return 'Fitting the memory bank…'
    case 'completed':
      return 'Done'
    case 'failed':
      return 'Failed'
    default:
      return job.value.status
  }
})

const progressColor = computed(() => {
  if (job.value?.status === 'failed') return 'error'
  if (job.value?.status === 'completed') return 'success'
  return 'primary'
})

async function onTeach() {
  if (!selectedModel.value || !fileCount.value) return
  await teach(selectedModel.value, files.value)
  files.value = []
}
</script>
