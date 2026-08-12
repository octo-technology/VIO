import { http } from '../../../shared/lib/http'
import { TrainingJobSchema } from '../../../entities/anomaly-bank/dtos/TrainingJobDto'
import type { TrainingJob } from '../../../entities/anomaly-bank/dtos/TrainingJobDto'
import { StationConfigSchema } from '../../../entities/station-config/dtos/StationConfigDto'

export async function addReferenceImages(modelName: string, files: File[]): Promise<TrainingJob> {
  const form = new FormData()
  for (const file of files) form.append('files', file)
  const res = await http.post(`/models/${encodeURIComponent(modelName)}/reference-images`, form)
  return TrainingJobSchema.parse(res.data)
}

export async function getTrainingJob(modelName: string, jobId: string): Promise<TrainingJob> {
  const res = await http.get(
    `/models/${encodeURIComponent(modelName)}/reference-images/jobs/${encodeURIComponent(jobId)}`,
  )
  return TrainingJobSchema.parse(res.data)
}

// Only models used by the active station config can be taught, since the
// orchestrator resolves a model's serving URL from that config.
export async function getTeachableModels(): Promise<string[]> {
  try {
    const res = await http.get('/configs/active')
    const config = StationConfigSchema.parse(res.data)
    const names = Object.values(config.pipeline_steps).map((step) => step.model_forwarder_config.model_name)
    return [...new Set(names)]
  } catch (e: any) {
    // 400 (no active config) / 404 (none set) simply mean nothing is teachable yet.
    if (e?.response?.status === 400 || e?.response?.status === 404) return []
    throw e
  }
}
