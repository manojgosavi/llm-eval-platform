import { useState, useEffect } from "react";
import { useParams, useNavigate } from 'react-router-dom'
import { getRunById, getScoresByRunId } from '../api/client'

function MetricRow({ label, value }) {
  return (
    <div className="flex justify-between py-2 border-b border-gray-100 last:border-0">
      <span className="text-sm text-gray-500">{label}</span>
      <span className="text-sm font-medium text-gray-900">{value}</span>
    </div>
  )
}


function ScoreCard({ score }) {
  const pct = Math.round(score.score * 100)
  const color = pct >= 70 ? 'text-green-600' : pct >= 40 ? 'text-yellow-600' : 'text-red-600'

  return (
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-medium uppercase tracking-wider text-gray-500">
            {score.scorer_type.replace('_', ' ')}
          </span>
          <span className={`text-xl font-bold ${color}`}>{pct}%</span>
        </div>
        {score.reasoning && (
          <p className="text-sm text-gray-600 mt-2">{score.reasoning}</p>
        )}
        {score.expected_output && (
          <div className="mt-3">
            <p className="text-xs text-gray-400 mb-1">Expected output</p>
            <p className="text-sm text-gray-600 bg-gray-50 rounded p-2">
              {score.expected_output}
            </p>
          </div>
        )}
        <p className="text-xs text-gray-400 mt-3">
          Scored {new Date(score.created_at).toLocaleString()}
        </p>
      </div>
    )
  }

  export default function RunDetail() {
  const { id }       = useParams()
  const navigate     = useNavigate()
  const [run, setRun]         = useState(null)
  const [scores, setScores]   = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError]     = useState(null)

  useEffect(() => {
    Promise.all([getRunById(id), getScoresByRunId(id)])
      .then(([runData, scoresData]) => {
        setRun(runData)
        setScores(Array.isArray(scoresData) ? scoresData : [])
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
  }, [id])

  if (loading) return (
    <div className="text-center py-12 text-gray-400 text-sm">Loading run...</div>
  )

  if (error) return (
    <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md text-sm">
      {error}
    </div>
  )

  if (!run) return null

  return (
    <div className="max-w-3xl space-y-6">

      {/* header */}
      <div className="flex items-center gap-4">
        <button
          onClick={() => navigate('/runs')}
          className="text-sm text-gray-500 hover:text-gray-900 transition-colors"
        >
          ← Back
        </button>
        <h1 className="text-xl font-semibold text-gray-900">Run #{run.id}</h1>
        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs
                         font-medium bg-blue-100 text-blue-800">
          {run.model.split('/')[1]}
        </span>
      </div>

      {/* prompt */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <p className="text-xs font-medium text-gray-400 uppercase tracking-wider mb-2">
          Prompt
        </p>
        <p className="text-sm text-gray-800 whitespace-pre-wrap">{run.prompt}</p>
      </div>

      {/* response */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <p className="text-xs font-medium text-gray-400 uppercase tracking-wider mb-2">
          Response
        </p>
        <p className="text-sm text-gray-800 whitespace-pre-wrap">{run.text}</p>
      </div>

      {/* metrics */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <p className="text-xs font-medium text-gray-400 uppercase tracking-wider mb-3">
          Metrics
        </p>
        <MetricRow label="Latency"          value={`${run.latency_ms.toFixed(0)}ms`} />
        <MetricRow label="Input tokens"     value={run.input_tokens} />
        <MetricRow label="Output tokens"    value={run.output_tokens} />
        <MetricRow label="Max tokens requested" value={run.max_tokens_requested} />
        <MetricRow label="Cost"             value={`$${run.cost_usd.toFixed(6)}`} />
        <MetricRow label="Context used"     value={`${run.context_used_pct}%`} />
        <MetricRow label="Truncated"        value={run.was_truncated ? 'Yes' : 'No'} />
        <MetricRow label="Created"          value={new Date(run.created_at).toLocaleString()} />
      </div>

      {/* scores */}
      <div>
        <p className="text-xs font-medium text-gray-400 uppercase tracking-wider mb-3">
          Scores {scores.length === 0 && '— none yet'}
        </p>
        {scores.length === 0 ? (
          <div className="bg-gray-50 rounded-lg border border-gray-200 px-4 py-8
                          text-center text-sm text-gray-400">
            No scores yet. Call POST /runs/{id}/score to evaluate this run.
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            {scores.map((s) => <ScoreCard key={s.id} score={s} />)}
          </div>
        )}
      </div>

    </div>
  )
}