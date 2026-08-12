import { z } from 'zod'

// The orchestrator returns this same shape both when a fit is accepted and when
// its progress is polled, so one schema covers both responses.
export const TrainingJobSchema = z.object({
  job_id: z.string(),
  model_name: z.string(),
  status: z.string(),
  total: z.number(),
  processed: z.number(),
  bank_size: z.number().nullable().optional(),
  error: z.string().nullable().optional(),
})

export type TrainingJob = z.infer<typeof TrainingJobSchema>

export const TERMINAL_STATUSES = ['completed', 'failed'] as const

export function isTerminal(status: string): boolean {
  return (TERMINAL_STATUSES as readonly string[]).includes(status)
}
