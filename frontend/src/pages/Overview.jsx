import { useState, useEffect } from 'react'
import { api } from '../api'
import KPICard from '../components/KPICard'
import Card from '../components/Card'
import Badge from '../components/Badge'

export default function Overview() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.getOverview()
      .then(setData)
      .catch(err => console.error('Overview fetch failed:', err))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="text-text-muted">Loading overview...</div>
  if (!data) return <div className="text-accent-red">Failed to load overview</div>

  const { kpis, action_emails, recent_notes, phase_summary } = data

  return (
    <div className="space-y-6">
      <h1 className="text-lg font-semibold">Overview</h1>

      {/* KPI Row */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        <KPICard label="Emails" value={kpis.emails.total} sub={`${kpis.emails.action_required} action`} color="#3b82f6" />
        <KPICard label="Clients" value={kpis.clients.total} sub={`${kpis.clients.active} active`} color="#10b981" />
        <KPICard label="Notes" value={kpis.notes.total} sub={`${kpis.notes.pending} pending`} color="#f59e0b" />
        <KPICard label="Use Cases" value={kpis.pipeline.total_ucs} sub={`${kpis.pipeline.avg_progress}% avg`} color="#8b5cf6" />
        <KPICard label="Repos" value={kpis.repos} color="#06b6d4" />
        <KPICard label="Elements" value={kpis.elements} sub="classified" color="#ef4444" />
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        {/* Action Emails */}
        <Card title="Action Required" icon="🔴" count={kpis.emails.action_required}>
          <div className="space-y-2">
            {action_emails?.map(email => (
              <div key={email.id} className="flex items-start gap-2 py-2 border-b border-border last:border-0">
                <Badge color={email.category === 'opportunity' ? 'amber' : email.category === 'client' ? 'green' : 'blue'}>
                  {email.category}
                </Badge>
                <div className="flex-1 min-w-0">
                  <div className="text-sm truncate">{email.subject}</div>
                  <div className="text-xs text-text-muted">{email.from_name}</div>
                </div>
              </div>
            ))}
            {(!action_emails || action_emails.length === 0) && (
              <div className="text-sm text-text-muted">No action items</div>
            )}
          </div>
        </Card>

        {/* Recent Notes */}
        <Card title="Recent Notes" icon="📝" count={kpis.notes.total}>
          <div className="space-y-2">
            {recent_notes?.map(note => (
              <div key={note.id} className="flex items-start gap-2 py-2 border-b border-border last:border-0">
                <Badge color={note.tag === 'action' ? 'red' : note.tag === 'research' ? 'blue' : 'gray'}>
                  {note.tag}
                </Badge>
                <div className="text-sm flex-1 truncate">{note.text}</div>
              </div>
            ))}
            {(!recent_notes || recent_notes.length === 0) && (
              <div className="text-sm text-text-muted">No notes yet</div>
            )}
          </div>
        </Card>
      </div>

      {/* Phase Summary */}
      <Card title="Pipeline Phase Summary" icon="🔬">
        <div className="flex flex-wrap gap-3">
          {Object.entries(phase_summary || {}).map(([phase, count]) => (
            <div key={phase} className="bg-bg-secondary rounded px-3 py-2 text-center">
              <div className="font-mono text-lg font-bold text-accent-blue">{count}</div>
              <div className="text-xs text-text-muted">{phase}</div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  )
}
