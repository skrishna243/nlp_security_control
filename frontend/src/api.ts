import type { NLResponse } from './types'

export async function executeCommand(text: string): Promise<NLResponse> {
  const correlationId = `fe-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`

  const res = await fetch('/nl/execute', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Correlation-ID': correlationId,
    },
    body: JSON.stringify({ text }),
  })

  if (!res.ok && res.status !== 400) {
    throw new Error(`HTTP ${res.status}: ${res.statusText}`)
  }

  return res.json()
}
