const EXAMPLES = [
  'arm the system',
  'please activate the alarm to stay mode',
  'turn off the alarm now',
  'add user John with pin 4321',
  'add a temporary user Sarah, pin 5678 from today 5pm to Sunday 10am',
  'remove user John',
  'show me all users',
  'My mother-in-law is coming to stay for the weekend, make sure she can arm and disarm our system using passcode 1234',
]

interface Props {
  onSelect: (cmd: string) => void
}

export function ExampleCommands({ onSelect }: Props) {
  return (
    <div style={{ marginBottom: '1rem' }}>
      <p style={{ fontSize: '0.75rem', color: '#94a3b8', marginBottom: '0.5rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
        Example commands
      </p>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
        {EXAMPLES.map(ex => (
          <button
            key={ex}
            onClick={() => onSelect(ex)}
            title={ex}
            style={{
              background: '#1e293b',
              border: '1px solid #334155',
              borderRadius: '6px',
              color: '#93c5fd',
              cursor: 'pointer',
              fontSize: '0.75rem',
              padding: '0.25rem 0.6rem',
              maxWidth: '220px',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
            }}
          >
            {ex}
          </button>
        ))}
      </div>
    </div>
  )
}
