export type Intent =
  | 'arm'
  | 'disarm'
  | 'add_user'
  | 'remove_user'
  | 'list_users'
  | null

export interface ParsedCommand {
  text: string
  intent: Intent
  source: 'rule' | 'llm'
  entities: {
    name?: string
    pin?: string
    mode?: 'away' | 'home' | 'stay'
    start_time?: string
    end_time?: string
    permissions?: string[]
  }
  api: {
    method: string
    path: string
    payload: Record<string, unknown> | null
  } | null
}

export interface NLResponse {
  ok: boolean
  parsed: ParsedCommand
  api_result: unknown | null
  error: string | null
}

export interface HistoryEntry {
  id: string
  timestamp: Date
  input: string
  response: NLResponse | null
  loading: boolean
  error: string | null
}
