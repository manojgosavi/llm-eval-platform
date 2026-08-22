import { useState, useEffect } from 'react'
import { getApiKeys, saveApiKeys, clearApiKeys } from '../hooks/useApiKeys'

export default function Settings() {
  const [keys, setKeys] = useState({
    anthropic: '',
    gemini: '',
    openai: '',
  })
  const [saved, setSaved] = useState(false)

  // load existing keys on mount
  useEffect(() => {
    const stored = getApiKeys()
    setKeys({
      anthropic: stored.anthropic || '',
      gemini:    stored.gemini    || '',
      openai:    stored.openai    || '',
    })
  }, [])

  function handleSave() {
    saveApiKeys(keys)
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  function handleClear() {
    clearApiKeys()
    setKeys({ anthropic: '', gemini: '', openai: '' })
  }

  return (
    <div className="max-w-xl space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-gray-900">API Keys</h1>
        <p className="text-sm text-gray-500 mt-1">
          Keys are stored in your browser's localStorage and sent as request
          headers over HTTPS. They are never stored on the server.
        </p>
      </div>

      <div className="bg-amber-50 border border-amber-200 rounded-md px-4 py-3 text-sm text-amber-800">
        <strong>Note:</strong> localStorage is vulnerable to XSS attacks.
        For production use, server-side encrypted key storage is recommended (MAN-44).
      </div>

      <div className="bg-white rounded-lg border border-gray-200 divide-y divide-gray-100">
        {[
          { key: 'anthropic', label: 'Anthropic (Claude)', placeholder: 'sk-ant-...' },
          { key: 'gemini',    label: 'Google (Gemini)',    placeholder: 'AIza...' },
          { key: 'openai',    label: 'OpenAI (GPT)',       placeholder: 'sk-...' },
        ].map(({ key, label, placeholder }) => (
          <div key={key} className="px-4 py-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {label}
            </label>
            <input
              type="password"
              value={keys[key]}
              onChange={(e) => setKeys((prev) => ({ ...prev, [key]: e.target.value }))}
              placeholder={placeholder}
              className="w-full text-sm border border-gray-300 rounded-md px-3 py-2
                         font-mono focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        ))}
      </div>

      <div className="flex gap-3">
        <button
          onClick={handleSave}
          className="px-4 py-2 text-sm font-medium text-white bg-blue-600
                     rounded-md hover:bg-blue-700 transition-colors"
        >
          {saved ? '✓ Saved' : 'Save keys'}
        </button>
        <button
          onClick={handleClear}
          className="px-4 py-2 text-sm font-medium text-gray-600 border
                     border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
        >
          Clear all
        </button>
      </div>
    </div>
  )
}