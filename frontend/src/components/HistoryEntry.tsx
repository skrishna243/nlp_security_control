import { useState } from 'react'
import type { HistoryEntry as Entry } from '../types'

const INTENT_COLORS: Record<string, string> = {
  arm: '#22c55e',
  disarm: '#f59e0b',
  add_user: '#3b82f6',
  remove_user: '#ef4444',
  list_users: '#a855f7',
}

const INTENT_LABELS: Record<string, string> = {
  arm: 'ARM SYSTEM',
  disarm: 'DISARM SYSTEM',
  add_user: 'ADD USER',
  remove_user: 'REMOVE USER',
  list_users: 'LIST USERS',
}

function formatRelativeTime(date: Date): string {
  const seconds = Math.floor((Date.now() - date.getTime()) / 1000)
  if (seconds < 5) return 'just now'
  if (seconds < 60) return `${seconds}s ago`
  const minutes = Math.floor(seconds / 60)
  if (minutes < 60) return `${minutes}m ago`
  return date.toLocaleTimeString()
}

interface Props {
  entry: Entry
}

export function HistoryEntry({ entry }: Props) {
  const [expanded, setExpanded] = useState(true)
  const { response } = entry

  const intent = response?.parsed?.intent
  const intentColor = intent ? (INTENT_COLORS[intent] ?? '#64748b') : '#64748b'
  const intentLabel = intent ? (INTENT_LABELS[intent] ?? intent) : 'UNKNOWN'

  return (
    <div
      style={{
        background: '#1e293b',
        border: `1px solid ${entry.error || (response && !response.ok) ? '#7f1d1d' : '#334155'}`,
        borderRadius: '8px',
        overflow: 'hidden',
        marginBottom: '0.75rem',
      }}
    >
      {/* Header */}
      <div
        onClick={() => setExpanded(e => !e)}
        style={{
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          gap: '0.75rem',
          padding: '0.75rem 1rem',
          background: '#16213e',
          userSelect: 'none',
        }}
      >
        <span
          style={{
            background: intentColor + '22',
            border: `1px solid ${intentColor}`,
            borderRadius: '4px',
            color: intentColor,
            fontSize: '0.65rem',
            fontWeight: 700,
            letterSpacing: '0.05em',
            padding: '0.15rem 0.4rem',
            minWidth: '90px',
            textAlign: 'center',
          }}
        >
          {entry.loading ? '...' : intentLabel}
        </span>
        <span style={{ flex: 1, color: '#cbd5e1', fontSize: '0.9rem', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
          {entry.input}
        </span>
        <span style={{ color: '#475569', fontSize: '0.75rem', flexShrink: 0 }}>
          {formatRelativeTime(entry.timestamp)}
        </span>
        <span style={{ color: '#475569', fontSize: '0.75rem' }}>{expanded ? '▲' : '▼'}</span>
      </div>

      {/* Expandable body */}
      {expanded && (
        <div style={{ padding: '0.75rem 1rem', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {/* Loading */}
          {entry.loading && (
            <p style={{ color: '#64748b', fontSize: '0.85rem' }}>Processing...</p>
          )}

          {/* Error */}
          {(entry.error || (response && !response.ok)) && (
            <Section title="Error" color="#ef4444">
              <Code>{entry.error ?? response?.error ?? 'Unknown error'}</Code>
            </Section>
          )}

          {/* NLP Interpretation */}
          {response && (
            <Section title={`NLP Interpretation • ${response.parsed.source === 'llm' ? '🤖 AI-assisted' : '⚡ Rule-based'}`} color="#94a3b8">
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '0.5rem' }}>
                <Badge label="Intent" value={response.parsed.intent ?? 'none'} color={intentColor} />
                {response.parsed.entities.name && (
                  <Badge label="Name" value={response.parsed.entities.name} color="#a78bfa" />
                )}
                {response.parsed.entities.pin && (
                  <Badge label="PIN" value={response.parsed.entities.pin} color="#fb923c" />
                )}
                {response.parsed.entities.mode && (
                  <Badge label="Mode" value={response.parsed.entities.mode} color="#34d399" />
                )}
                {response.parsed.entities.permissions && (
                  <Badge label="Perms" value={response.parsed.entities.permissions.join('+')} color="#60a5fa" />
                )}
                {response.parsed.entities.start_time && (
                  <Badge label="From" value={new Date(response.parsed.entities.start_time).toLocaleString()} color="#f472b6" />
                )}
                {response.parsed.entities.end_time && (
                  <Badge label="To" value={new Date(response.parsed.entities.end_time).toLocaleString()} color="#f472b6" />
                )}
              </div>
            </Section>
          )}

          {/* API Call */}
          {response?.parsed.api && (
            <Section title="API Call" color="#94a3b8">
              <Code>
                {response.parsed.api.method} {response.parsed.api.path}
                {response.parsed.api.payload
                  ? '\n' + JSON.stringify(response.parsed.api.payload, null, 2)
                  : ''}
              </Code>
            </Section>
          )}

          {/* API Response */}
          {response?.api_result !== null && response?.api_result !== undefined && (
            <Section title="Response" color="#94a3b8">
              <Code>{JSON.stringify(response.api_result, null, 2)}</Code>
            </Section>
          )}
        </div>
      )}
    </div>
  )
}

function Section({ title, color, children }: { title: string; color: string; children: React.ReactNode }) {
  return (
    <div>
      <p style={{ color, fontSize: '0.7rem', fontWeight: 600, letterSpacing: '0.05em', marginBottom: '0.3rem', textTransform: 'uppercase' }}>
        {title}
      </p>
      {children}
    </div>
  )
}

function Badge({ label, value, color }: { label: string; value: string; color: string }) {
  return (
    <span style={{
      background: color + '18',
      border: `1px solid ${color}44`,
      borderRadius: '4px',
      fontSize: '0.75rem',
      padding: '0.2rem 0.5rem',
    }}>
      <span style={{ color: '#94a3b8' }}>{label}: </span>
      <span style={{ color }}>{value}</span>
    </span>
  )
}

function Code({ children }: { children: React.ReactNode }) {
  return (
    <pre style={{
      background: '#0f172a',
      borderRadius: '6px',
      color: '#cbd5e1',
      fontSize: '0.78rem',
      lineHeight: '1.5',
      overflow: 'auto',
      padding: '0.5rem 0.75rem',
      whiteSpace: 'pre-wrap',
      wordBreak: 'break-word',
    }}>
      {children}
    </pre>
  )
}
