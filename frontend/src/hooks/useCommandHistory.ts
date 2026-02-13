import { useState, useCallback } from 'react'
import type { HistoryEntry, NLResponse } from '../types'
import { executeCommand } from '../api'

// Inline UUID v4 without dependency
function genId(): string {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`
}

export function useCommandHistory() {
  const [entries, setEntries] = useState<HistoryEntry[]>([])
  const [isLoading, setIsLoading] = useState(false)

  const submit = useCallback(async (text: string) => {
    if (!text.trim()) return

    const id = genId()
    const entry: HistoryEntry = {
      id,
      timestamp: new Date(),
      input: text,
      response: null,
      loading: true,
      error: null,
    }

    setEntries(prev => [entry, ...prev])
    setIsLoading(true)

    try {
      const response = await executeCommand(text)
      setEntries(prev =>
        prev.map(e =>
          e.id === id ? { ...e, response, loading: false } : e
        )
      )
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Unknown error'
      setEntries(prev =>
        prev.map(e =>
          e.id === id ? { ...e, error: errorMsg, loading: false } : e
        )
      )
    } finally {
      setIsLoading(false)
    }
  }, [])

  const clear = useCallback(() => setEntries([]), [])

  return { entries, isLoading, submit, clear }
}
