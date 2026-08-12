import { ref, computed } from 'vue'
import * as referenceBankRepository from '../api/referenceBankRepository'
import { isTerminal } from '../../../entities/anomaly-bank/dtos/TrainingJobDto'
import type { TrainingJob } from '../../../entities/anomaly-bank/dtos/TrainingJobDto'

const POLL_INTERVAL_MS = 500
// Fitting a bank runs on the serving backend and can take minutes on the first,
// cold, backbone download; give the poll a generous ceiling.
const POLL_TIMEOUT_MS = 300_000

export function useReferenceBank() {
  const uploading = ref(false)
  const job = ref<TrainingJob | null>(null)

  const progress = computed(() => {
    const current = job.value
    if (!current || current.total === 0) return 0
    return Math.round((current.processed / current.total) * 100)
  })

  async function teach(modelName: string, files: File[]): Promise<TrainingJob | null> {
    uploading.value = true
    job.value = null
    try {
      const accepted = await referenceBankRepository.addReferenceImages(modelName, files)
      job.value = accepted

      const deadline = Date.now() + POLL_TIMEOUT_MS
      while (!isTerminal(job.value.status) && Date.now() < deadline) {
        await new Promise((resolve) => setTimeout(resolve, POLL_INTERVAL_MS))
        try {
          job.value = await referenceBankRepository.getTrainingJob(modelName, accepted.job_id)
        } catch {
          // Transient polling error — keep trying until the deadline.
        }
      }
      return job.value
    } finally {
      uploading.value = false
    }
  }

  return { uploading, job, progress, teach }
}
