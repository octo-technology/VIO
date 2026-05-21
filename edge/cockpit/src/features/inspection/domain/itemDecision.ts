export interface Item {
  id: string
  creation_date?: string
  state: string
  decision?: string | null
}

export function itemChipColor(item: Item): string {
  if (item.state === 'ERROR') return 'error'
  if (item.state === 'DONE') return item.decision === 'OK' ? 'success' : 'error'
  return 'warning'
}

export function itemChipLabel(item: Item): string {
  if (item.state === 'ERROR') return 'ERROR'
  if (item.state === 'DONE') return item.decision ?? item.state
  return item.state
}
