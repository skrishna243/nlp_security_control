import { useState, useEffect, KeyboardEvent } from 'react'

interface Props {
  onSubmit: (text: string) => void
  isLoading: boolean
  externalValue?: string
}

export function CommandInput({ onSubmit, isLoading, externalValue = '' }: Props) {
  const [value, setValue] = useState('')

  // Sync when parent sets an example command
  useEffect(() => {
    if (externalValue) setValue(externalValue)
  }, [externalValue])

  const handleSubmit = () => {
    const trimmed = value.trim()
    if (!trimmed || isLoading) return
    onSubmit(trimmed)
    setValue('')
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault()
      handleSubmit()
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
      <textarea
        value={value}
        onChange={e => setValue(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Type a command in natural language... (Ctrl+Enter to submit)"
        rows={3}
        style={{
          background: '#1e293b',
          border: '1px solid #334155',
          borderRadius: '8px',
          color: '#e2e8f0',
          fontSize: '0.95rem',
          padding: '0.75rem 1rem',
          resize: 'vertical',
          outline: 'none',
          width: '100%',
          fontFamily: 'inherit',
          lineHeight: '1.5',
        }}
        disabled={isLoading}
      />
      <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem' }}>
        <span style={{ fontSize: '0.75rem', color: '#64748b', alignSelf: 'center' }}>
          Ctrl+Enter to submit
        </span>
        <button
          onClick={handleSubmit}
          disabled={isLoading || !value.trim()}
          style={{
            background: isLoading || !value.trim() ? '#334155' : '#3b82f6',
            border: 'none',
            borderRadius: '6px',
            color: isLoading || !value.trim() ? '#64748b' : '#fff',
            cursor: isLoading || !value.trim() ? 'not-allowed' : 'pointer',
            fontSize: '0.9rem',
            fontWeight: 600,
            padding: '0.5rem 1.25rem',
            transition: 'background 0.15s',
          }}
        >
          {isLoading ? 'Processing...' : 'Send'}
        </button>
      </div>
    </div>
  )
}
