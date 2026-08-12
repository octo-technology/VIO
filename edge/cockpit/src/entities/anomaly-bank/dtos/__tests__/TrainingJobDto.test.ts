import { describe, it, expect } from 'vitest'
import { TrainingJobSchema, isTerminal } from '../TrainingJobDto'

const ACCEPTED_JOB = {
  job_id: 'job-1',
  model_name: 'my_part',
  status: 'pending',
  total: 4,
  processed: 0,
}

describe('TrainingJobSchema', () => {
  it('parses an accepted job with no bank_size/error yet', () => {
    const result = TrainingJobSchema.safeParse(ACCEPTED_JOB)
    expect(result.success).toBe(true)
  })

  it('parses a completed job with a bank_size', () => {
    const result = TrainingJobSchema.safeParse({ ...ACCEPTED_JOB, status: 'completed', processed: 4, bank_size: 10 })
    expect(result.success).toBe(true)
  })

  it('accepts a null error', () => {
    const result = TrainingJobSchema.safeParse({ ...ACCEPTED_JOB, error: null })
    expect(result.success).toBe(true)
  })

  it('rejects a job missing required fields', () => {
    const result = TrainingJobSchema.safeParse({ job_id: 'x', status: 'pending' })
    expect(result.success).toBe(false)
  })
})

describe('isTerminal', () => {
  it('is true for completed and failed', () => {
    expect(isTerminal('completed')).toBe(true)
    expect(isTerminal('failed')).toBe(true)
  })

  it('is false for in-flight statuses', () => {
    expect(isTerminal('pending')).toBe(false)
    expect(isTerminal('running')).toBe(false)
  })
})
