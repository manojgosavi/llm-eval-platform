// frontend/src/pages/RunHistory.jsx

import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { getRuns } from '../api/client'

const MODEL_OPTIONS = [
  { value: '',                          label: 'All models' },
  { value: 'anthropic/claude-sonnet-4-6', label: 'Claude Sonnet' },
  { value: 'gemini/gemini-3.5-flash',   label: 'Gemini 3.5 Flash' },
  { value: 'openai/gpt-4o-mini',        label: 'GPT-4o Mini' },
]

export default function RunHistory() {
  const [runs, setRuns]       = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError]     = useState(null)
  const [model, setModel]     = useState('')
  const navigate              = useNavigate()

  useEffect(() => {
    setLoading(true)
    setError(null)
    getRuns({ model: model || undefined, limit: 50 })
      .then((data) => {
        console.log('API response:', data)
        setRuns(data)
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [model])  // re-fetch whenever model filter changes

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-semibold text-gray-900">Run History</h1>

        {/* model filter */}
        <select
          value={model}
          onChange={(e) => setModel(e.target.value)}
          className="text-sm border border-gray-300 rounded-md px-3 py-1.5
                     text-gray-700 bg-white focus:outline-none focus:ring-2
                     focus:ring-blue-500"
        >
          {MODEL_OPTIONS.map((o) => (
            <option key={o.value} value={o.value}>{o.label}</option>
          ))}
        </select>
      </div>

      {/* loading state */}
      {loading && (
        <div className="text-center py-12 text-gray-400 text-sm">Loading runs...</div>
      )}

      {/* error state */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3
                        rounded-md text-sm mb-4">
          {error}
        </div>
      )}

      {/* empty state */}
      {!loading && !error && runs.length === 0 && (
        <div className="text-center py-12 text-gray-400 text-sm">
          No runs yet. Use the API to create your first run.
        </div>
      )}

      {/* table */}
      {!loading && runs.length > 0 && (
        <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                {['ID', 'Model', 'Prompt', 'Latency', 'Cost', 'Truncated', 'Created'].map(
                  (h) => (
                    <th
                      key={h}
                      className="px-4 py-3 text-left text-xs font-medium
                                 text-gray-500 uppercase tracking-wider"
                    >
                      {h}
                    </th>
                  )
                )}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {runs.map((run) => (
                <tr
                  key={run.id}
                  onClick={() => navigate(`/runs/${run.id}`)}
                  className="hover:bg-blue-50 cursor-pointer transition-colors"
                >
                  <td className="px-4 py-3 text-gray-500 font-mono">#{run.id}</td>
                  <td className="px-4 py-3">
                    <span className="inline-flex items-center px-2 py-0.5 rounded
                                     text-xs font-medium bg-blue-100 text-blue-800">
                      {run.model.split('/')[1]}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-gray-700 max-w-xs truncate">
                    {run.prompt}
                  </td>
                  <td className="px-4 py-3 text-gray-600 font-mono">
                    {run.latency_ms.toFixed(0)}ms
                  </td>
                  <td className="px-4 py-3 text-gray-600 font-mono">
                    ${run.cost_usd.toFixed(5)}
                  </td>
                  <td className="px-4 py-3">
                    <span className={`inline-flex items-center px-2 py-0.5 rounded
                                      text-xs font-medium ${
                                        run.was_truncated
                                          ? 'bg-red-100 text-red-700'
                                          : 'bg-green-100 text-green-700'
                                      }`}>
                      {run.was_truncated ? 'Yes' : 'No'}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-gray-500 text-xs">
                    {new Date(run.created_at).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}