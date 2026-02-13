import type { HistoryEntry as Entry } from '../types'
import { HistoryEntry } from './HistoryEntry'

interface Props {
  entries: Entry[]
  onClear: () => void
}

export function CommandHistory({ entries, onClear }: Props) {
  if (entries.length === 0) {
    return (
      <div style={{
        textAlign: 'center',
        color: '#475569',
        fontSize: '0.9rem',
        padding: '3rem 0',
        borderTop: '1px solid #1e293b',
        marginTop: '1rem',
      }}>
        No commands yet. Try one of the examples above or type your own.
      </div>
    )
  }

  return (
    <div style={{ marginTop: '1rem' }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        borderBottom: '1px solid #1e293b',
        marginBottom: '1rem',
        paddingBottom: '0.5rem',
      }}>
        <span style={{ color: '#64748b', fontSize: '0.8rem' }}>
          {entries.length} command{entries.length !== 1 ? 's' : ''}
        </span>
        <button
          onClick={onClear}
          style={{
            background: 'transparent',
            border: '1px solid #334155',
            borderRadius: '4px',
            color: '#64748b',
            cursor: 'pointer',
            fontSize: '0.75rem',
            padding: '0.2rem 0.6rem',
          }}
        >
          Clear history
        </button>
      </div>
      {entries.map(entry => (
        <HistoryEntry key={entry.id} entry={entry} />
      ))}
    </div>
  )
}
