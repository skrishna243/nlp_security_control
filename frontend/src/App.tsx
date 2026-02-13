import { useState } from 'react'
import { CommandInput } from './components/CommandInput'
import { CommandHistory } from './components/CommandHistory'
import { ExampleCommands } from './components/ExampleCommands'
import { useCommandHistory } from './hooks/useCommandHistory'

export default function App() {
  const { entries, isLoading, submit, clear } = useCommandHistory()
  const [inputValue, setInputValue] = useState('')

  const handleExampleSelect = (cmd: string) => {
    setInputValue(cmd)
  }

  const handleSubmit = (text: string) => {
    setInputValue('')
    submit(text)
  }

  return (
    <div style={{
      maxWidth: '800px',
      margin: '0 auto',
      padding: '2rem 1rem',
      minHeight: '100vh',
    }}>
      {/* Header */}
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{
          color: '#f1f5f9',
          fontSize: '1.5rem',
          fontWeight: 700,
          marginBottom: '0.25rem',
        }}>
          NL Security Control
        </h1>
        <p style={{ color: '#64748b', fontSize: '0.875rem' }}>
          Control your security system with natural language commands
        </p>
      </div>

      {/* Example commands */}
      <ExampleCommands onSelect={handleExampleSelect} />

      {/* Command input */}
      <CommandInput
        onSubmit={handleSubmit}
        isLoading={isLoading}
        externalValue={inputValue}
      />

      {/* History */}
      <CommandHistory entries={entries} onClear={clear} />
    </div>
  )
}
