import { useState, useEffect } from 'react'
import { api } from '../api'
import Card from '../components/Card'
import Badge from '../components/Badge'
import ProgressBar from '../components/ProgressBar'

const PHASE_COLORS = {
  'Phase 0': '#3b82f6', 'Phase 1': '#f59e0b',
  'Phase 2': '#10b981', 'Phase 3': '#8b5cf6',
}

const TYPE_COLORS = {
  photonic_ir: '#ef4444', acoustic_resonator: '#f59e0b',
  rf_transceiver: '#06b6d4', inertial_sensor: '#8b5cf6',
  quantum_sensing: '#10b981',
}

export default function Pipeline() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.getPipeline()
      .then(setData)
      .catch(err => console.error('Pipeline fetch failed:', err))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="text-text-muted">Loading pipeline...</div>

  const { pipeline = [], categories = [], phases = {} } = data || {}

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-semibold">Pipeline Status</h1>
        <span className="font-mono text-xs text-text-muted">{pipeline.length} UCs</span>
      </div>

      {/* Phase summary */}
      <div className="flex flex-wrap gap-3">
        {Object.entries(phases).map(([phase, count]) => (
          <div key={phase} className="bg-bg-card border border-border rounded-lg px-4 py-2 text-center"
               style={{ borderLeft: `3px solid ${PHASE_COLORS[phase] || '#64748b'}` }}>
            <div className="font-mono text-xl font-bold" style={{ color: PHASE_COLORS[phase] || '#64748b' }}>{count}</div>
            <div className="text-xs text-text-muted">{phase}</div>
          </div>
        ))}
      </div>

      {/* UC Category groups */}
      {categories.map(cat => (
        <Card key={cat.cat} title={cat.cat} count={cat.ucs.length}>
          <div className="space-y-2">
            {pipeline.filter(uc => cat.ucs.includes(uc.uc)).map(uc => (
              <div key={uc.uc} className="flex items-center gap-3 py-2 border-b border-border last:border-0">
                <span className="font-mono text-xs font-bold w-12 shrink-0" style={{ color: cat.color }}>{uc.uc}</span>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-sm truncate">{uc.name}</span>
                    <Badge color={uc.phase === 'Phase 1' ? 'amber' : 'blue'}>{uc.phase}</Badge>
                  </div>
                  <div className="flex items-center gap-2 mt-1">
                    <ProgressBar value={uc.progress} color={cat.color} />
                    <span className="font-mono text-xs text-text-muted w-10 text-right shrink-0">{uc.progress}%</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      ))}
    </div>
  )
}
