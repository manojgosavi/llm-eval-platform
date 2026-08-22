import { useState, useEffect} from 'react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, Legend
} from 'recharts'
import {getRuns} from '../api/client'

function aggregateRunsByModel(runs) {
  const grouped = runs.reduce((acc, run) => {
    const key = run.model.split('/')[1]
    if (!acc[key]) acc[key] = { latencies: [], costs: [], count: 0}
    acc[key].latencies.push(run.latency_ms)
    acc[key].costs.push(run.cost_usd)
    acc[key].count += 1
    return acc
    }, {})

    return Object.entries(grouped).map(([model, data]) => ({
      model,
      avg_latency: Math.round(
        data.latencies.reduce((a, b) => a + b, 0) / data.latencies.length
      ),
      avg_cost: parseFloat(
        (data.costs.reduce((a, b) => a + b, 0) / data.costs.length)
      .toFixed(5)
      ),
      run_count: data.count,
    }))
  }

  function aggregateRunsOverTime(runs) {
    const grouped = runs.reduce((acc, run) => {
      const date = new Date(run.created_at).toLocaleDateString()
      acc[date] = (acc[date] || 0) + 1
      return acc
    }, {})
    return Object.entries(grouped)
      .map(([date, count]) => ({ date, count }))
      .sort((a,b) => new Date(a.date) - new Date(b.date))
  }

  function StatCard({ label, value }) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 px-6 py-4">
      <p className="text-sm text-gray-500">{label}</p>
      <p className="text-2xl font-semibold text-gray-900 mt-1">{value}</p>
    </div>
    )
  }

  export default function Dashboard(){
    const [runs, setRuns] = useState([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    useEffect(() => {
      getRuns({ limit : 200})
      .then((data) => setRuns(Array.isArray(data) ? data : []))
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false))
    }, [])

    if (loading) return (
      <div className="text-center py-12 text-gray-400 text-sm">Loading runs...</div>
    )

    if (error) return (
    <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3
                    rounded-md text-sm">
      {error}
    </div>
  )

  if (runs.length === 0) return (
    <div className="text-center py-12 text-gray-400 text-sm">
      No runs yet. Create your first run via the API.
    </div>
  )

  const modelData   = aggregateRunsByModel(runs)
  const timeData    = aggregateRunsOverTime(runs)
  const totalCost   = runs.reduce((a, b) => a + b.cost_usd, 0).toFixed(4)
  const avgLatency  = Math.round(runs.reduce((a, b) => a + b.latency_ms, 0) / runs.length)
  const truncated   = runs.filter((r) => r.was_truncated).length

  return (
    <div className="space-y-8">
      <h1 className="text-xl font-semibold text-gray-900">Dashboard</h1>

      {/* stat cards */}
      <div className="grid grid-cols-4 gap-4">
        <StatCard label="Total Runs"       value={runs.length} />
        <StatCard label="Total Cost"       value={`$${totalCost}`} />
        <StatCard label="Avg Latency"      value={`${avgLatency}ms`} />
        <StatCard label="Truncated Runs"   value={truncated} />
      </div>

      {/* latency by model */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h2 className="text-sm font-medium text-gray-700 mb-4">
          Avg Latency by Model (ms)
        </h2>
        <ResponsiveContainer width="100%" height={240}>
          <BarChart data={modelData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="model" tick={{ fontSize: 12 }} />
            <YAxis tick={{ fontSize: 12 }} />
            <Tooltip formatter={(v) => [`${v}ms`, 'Avg Latency']} />
            <Bar dataKey="avg_latency" fill="#6366f1" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* cost by model */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h2 className="text-sm font-medium text-gray-700 mb-4">
          Avg Cost by Model (USD)
        </h2>
        <ResponsiveContainer width="100%" height={240}>
          <BarChart data={modelData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="model" tick={{ fontSize: 12 }} />
            <YAxis tick={{ fontSize: 12 }} tickFormatter={(v) => `$${v}`} />
            <Tooltip formatter={(v) => [`$${v}`, 'Avg Cost']} />
            <Bar dataKey="avg_cost" fill="#10b981" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* runs over time */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h2 className="text-sm font-medium text-gray-700 mb-4">
          Runs Over Time
        </h2>
        <ResponsiveContainer width="100%" height={240}>
          <LineChart data={timeData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="date" tick={{ fontSize: 12 }} />
            <YAxis tick={{ fontSize: 12 }} />
            <Tooltip />
            <Legend />
            <Line
              type="monotone"
              dataKey="count"
              stroke="#6366f1"
              strokeWidth={2}
              dot={{ r: 4 }}
              name="Runs"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
  }