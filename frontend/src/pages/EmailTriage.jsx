import { useState, useEffect } from 'react'
import { api } from '../api'
import Card from '../components/Card'
import Badge from '../components/Badge'
import EmailDrawer from '../components/EmailDrawer'

const CAT_COLORS = {
  research: 'blue', client: 'green', opportunity: 'amber',
  business: 'purple', noise: 'gray',
}

export default function EmailTriage() {
  const [data, setData] = useState(null)
  const [filter, setFilter] = useState(null)
  const [loading, setLoading] = useState(true)
  const [syncing, setSyncing] = useState(false)
  const [selectedEmail, setSelectedEmail] = useState(null)

  const fetchEmails = (cat) => {
    const params = {}
    if (cat) params.category = cat
    return api.getEmails(params).then(setData)
  }

  useEffect(() => {
    fetchEmails(filter)
      .catch(err => console.error('Email fetch failed:', err))
      .finally(() => setLoading(false))
  }, [filter])

  const handleSync = async () => {
    setSyncing(true)
    try {
      await api.syncEmails()
      await fetchEmails(filter)
    } catch (err) {
      console.error('Sync failed:', err)
    } finally {
      setSyncing(false)
    }
  }

  const handleEmailUpdate = (updated) => {
    // Refresh the email in the list without full reload
    setData(prev => {
      if (!prev) return prev
      const emails = prev.emails.map(e =>
        e.id === updated.id ? updated : e
      )
      return { ...prev, emails }
    })
    // Also update the drawer's copy
    setSelectedEmail(updated)
  }

  if (loading) return <div className="text-text-muted">Loading emails...</div>

  const { emails = [], counts = {} } = data || {}

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-semibold">Email Triage</h1>
        <button
          onClick={handleSync}
          disabled={syncing}
          className="px-3 py-1.5 bg-accent-blue/20 text-accent-blue text-xs rounded hover:bg-accent-blue/30 disabled:opacity-50"
        >
          {syncing ? 'Syncing...' : 'Sync Gmail'}
        </button>
      </div>

      {/* Category filters */}
      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => setFilter(null)}
          className={`px-3 py-1 text-xs rounded border ${!filter ? 'border-accent-blue text-accent-blue bg-accent-blue/10' : 'border-border text-text-muted hover:text-text-primary'}`}
        >
          All ({Object.values(counts).reduce((a, b) => a + b, 0)})
        </button>
        {Object.entries(counts).map(([cat, count]) => (
          <button
            key={cat}
            onClick={() => setFilter(cat)}
            className={`px-3 py-1 text-xs rounded border ${filter === cat ? 'border-accent-blue text-accent-blue bg-accent-blue/10' : 'border-border text-text-muted hover:text-text-primary'}`}
          >
            {cat} ({count})
          </button>
        ))}
      </div>

      {/* Email list */}
      <Card title="Inbox" icon="&#128231;" count={emails.length}>
        <div className="space-y-0">
          {emails.map(email => (
            <div
              key={email.id}
              onClick={() => setSelectedEmail(email)}
              className="flex items-start gap-3 py-3 border-b border-border last:border-0 hover:bg-bg-hover px-2 -mx-2 rounded cursor-pointer"
            >
              <div className="flex flex-col items-center gap-1 pt-1 shrink-0">
                {email.urgency === 'respond' && <span className="w-2.5 h-2.5 rounded-full bg-accent-red" title="Respond" />}
                {email.urgency === 'review' && <span className="w-2.5 h-2.5 rounded-full bg-amber-400" title="Review" />}
                {email.urgency === 'archive' && <span className="w-2.5 h-2.5 rounded-full bg-accent-blue" title="Archive" />}
                {!email.urgency && email.action_required && <span className="w-2.5 h-2.5 rounded-full bg-accent-red" title="Action Required" />}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <Badge color={CAT_COLORS[email.category] || 'gray'}>{email.category}</Badge>
                  {email.uc && <Badge color="purple">{email.uc}</Badge>}
                  {email.client && <Badge color="cyan">{email.client}</Badge>}
                  {email.has_attachment && <span className="text-xs">&#128206;</span>}
                </div>
                <div className="text-sm font-medium truncate">{email.subject}</div>
                <div className="flex items-center gap-2 mt-0.5">
                  <span className="text-xs text-text-secondary">{email.from_name}</span>
                  <span className="text-xs text-text-muted">{email.date?.split('T')[0]}</span>
                </div>
                <div className="text-xs text-text-muted mt-1 truncate">{email.snippet}</div>
              </div>
            </div>
          ))}
          {emails.length === 0 && <div className="text-sm text-text-muted py-4 text-center">No emails</div>}
        </div>
      </Card>

      {/* Email detail drawer */}
      {selectedEmail && (
        <EmailDrawer
          email={selectedEmail}
          onClose={() => setSelectedEmail(null)}
          onUpdate={handleEmailUpdate}
        />
      )}
    </div>
  )
}
