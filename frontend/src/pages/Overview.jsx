import { useState, useEffect } from 'react'
import { api } from '../api'
import KPICard from '../components/KPICard'
import Card from '../components/Card'
import Badge from '../components/Badge'

function formatGreeting() {
  const hour = new Date().getHours()
  if (hour < 12) return 'Good morning'
  if (hour < 17) return 'Good afternoon'
  return 'Good evening'
}

function formatDate() {
  return new Date().toLocaleDateString('en-US', {
    weekday: 'long', month: 'long', day: 'numeric',
  })
}

function formatTime() {
  return new Date().toLocaleTimeString('en-US', {
    hour: 'numeric', minute: '2-digit',
  })
}

export default function Overview() {
  const [data, setData] = useState(null)
  const [digest, setDigest] = useState(null)
  const [brief, setBrief] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      api.getOverview(),
      api.getAgentDigest().catch(() => null),
      api.getNotes({ tag: 'action', limit: 5 }).catch(() => null),
    ])
      .then(([overview, dig, notesData]) => {
        setData(overview)
        setDigest(dig)
        // Find latest morning brief note
        const notes = notesData?.notes || []
        const briefNote = notes.find(n =>
          n.text && n.text.startsWith('[Morning Brief')
        )
        setBrief(briefNote)
      })
      .catch(err => console.error('Overview fetch failed:', err))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="text-text-muted">Loading...</div>
  if (!data) return <div className="text-accent-red">Failed to load</div>

  const { kpis, action_emails, recent_notes, phase_summary } = data
  const actionItems = digest?.action_items || []

  return (
    <div className="space-y-6">
      {/* Greeting header */}
      <div>
        <h1 className="text-lg font-semibold">
          {formatGreeting()}, Sal.
        </h1>
        <div className="text-xs text-text-muted">
          {formatDate()} &middot; {formatTime()}
        </div>
      </div>

      {/* Morning Brief */}
      {brief && (
        <Card title="Morning Brief" icon="&#9728;">
          <div className="text-sm text-text-secondary leading-relaxed whitespace-pre-wrap">
            {brief.text.replace(/^\[Morning Brief[^\]]*\]\n*/, '')}
          </div>
        </Card>
      )}

      {/* Three-column layout */}
      <div className="grid md:grid-cols-3 gap-4">
        {/* TODAY */}
        <Card title="Today" icon="&#128308;">
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-accent-red" />
              <span className="text-sm font-medium">
                {kpis.emails.action_required} Respond
              </span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-amber-400" />
              <span className="text-sm">
                {(kpis.emails.total || 0) - (kpis.emails.action_required || 0)} Review
              </span>
            </div>
            <div className="text-xs text-text-muted mt-2">
              Pipeline: {kpis.pipeline.total_ucs} UCs &middot; {kpis.pipeline.avg_progress}% avg
            </div>
            <div className="text-xs text-text-muted">
              {kpis.notes.pending} pending notes
            </div>
          </div>
        </Card>

        {/* THIS WEEK */}
        <Card title="This Week" icon="&#128197;">
          <div className="space-y-3">
            <div className="text-sm">
              <span className="font-medium">{kpis.emails.total}</span>
              <span className="text-text-muted"> emails</span>
            </div>
            <div className="text-sm">
              <span className="font-medium">{kpis.clients.active}</span>
              <span className="text-text-muted"> active clients</span>
            </div>
            {Object.entries(phase_summary || {}).map(([phase, count]) => (
              <div key={phase} className="flex items-center justify-between text-xs">
                <span className="text-text-secondary">{phase}</span>
                <span className="font-mono text-accent-blue">{count}</span>
              </div>
            ))}
          </div>
        </Card>

        {/* WATCHING */}
        <Card title="Watching" icon="&#128065;">
          <div className="space-y-2">
            {actionItems.length > 0 ? (
              actionItems.slice(0, 4).map((item, i) => (
                <div key={i} className="py-1.5 border-b border-border last:border-0">
                  <div className="text-sm truncate">{item.subject}</div>
                  <div className="text-xs text-text-muted">
                    {item.sender} &middot; {item.category}
                  </div>
                  {item.summary && (
                    <div className="text-xs text-text-secondary mt-0.5 line-clamp-1">
                      {item.summary}
                    </div>
                  )}
                </div>
              ))
            ) : (
              // Fall back to action emails from overview
              action_emails?.slice(0, 4).map(email => (
                <div key={email.id} className="py-1.5 border-b border-border last:border-0">
                  <div className="text-sm truncate">{email.subject}</div>
                  <div className="text-xs text-text-muted">{email.from_name}</div>
                </div>
              ))
            )}
            {actionItems.length === 0 && (!action_emails || action_emails.length === 0) && (
              <div className="text-sm text-text-muted">Nothing urgent</div>
            )}
          </div>
        </Card>
      </div>

      {/* KPI Row — compact */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        <KPICard label="Emails" value={kpis.emails.total} sub={kpis.emails.action_required + ' action'} color="#3b82f6" />
        <KPICard label="Clients" value={kpis.clients.total} sub={kpis.clients.active + ' active'} color="#10b981" />
        <KPICard label="Notes" value={kpis.notes.total} sub={kpis.notes.pending + ' pending'} color="#f59e0b" />
        <KPICard label="Use Cases" value={kpis.pipeline.total_ucs} sub={kpis.pipeline.avg_progress + '% avg'} color="#8b5cf6" />
        <KPICard label="Elements" value={kpis.elements} sub="classified" color="#ef4444" />
      </div>

      {/* Recent Notes */}
      <Card title="Recent Notes" icon="&#128221;" count={kpis.notes.total}>
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
  )
}
