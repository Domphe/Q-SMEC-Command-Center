import { useState, useEffect } from 'react'
import { api } from '../api'
import Badge from './Badge'

const CAT_COLORS = {
  research: 'blue', client: 'green', opportunity: 'amber',
  business: 'purple', noise: 'gray',
}

export default function ClientDrawer({ client, onClose, onEmailClick }) {
  const [emails, setEmails] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const handler = (e) => { if (e.key === 'Escape') onClose() }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [onClose])

  useEffect(() => {
    if (!client) return
    setLoading(true)
    api.getClientEmails(client.id)
      .then(res => setEmails(res.emails || []))
      .catch(() => setEmails([]))
      .finally(() => setLoading(false))
  }, [client])

  if (!client) return null

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/40 z-40"
        onClick={onClose}
      />

      {/* Drawer */}
      <div className="fixed top-0 right-0 h-full w-full md:w-96 bg-bg-secondary border-l border-border z-50 flex flex-col shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-border shrink-0">
          <span className="text-sm font-semibold truncate">{client.name}</span>
          <button
            onClick={onClose}
            className="text-text-muted hover:text-text-primary text-lg leading-none"
          >
            &times;
          </button>
        </div>

        {/* Client info */}
        <div className="px-4 py-3 border-b border-border shrink-0 space-y-1">
          <div className="flex gap-2">
            <Badge color={client.status === 'active' ? 'green' : client.status === 'prospect' ? 'amber' : 'gray'}>
              {client.status}
            </Badge>
            <Badge color={client.priority === 'high' ? 'red' : 'amber'}>
              {client.priority}
            </Badge>
          </div>
          {client.contact && (
            <div className="text-xs text-text-secondary">
              Contact: {client.contact}
            </div>
          )}
          {client.sector && (
            <div className="text-xs text-text-muted">{client.sector}</div>
          )}
        </div>

        {/* Email timeline */}
        <div className="flex-1 overflow-y-auto p-4">
          <div className="text-xs text-text-muted mb-3 font-medium uppercase tracking-wide">
            Email Timeline ({emails.length})
          </div>
          {loading ? (
            <div className="text-sm text-text-muted">Loading...</div>
          ) : emails.length > 0 ? (
            <div className="space-y-0">
              {emails.map(email => (
                <div
                  key={email.id}
                  onClick={() => onEmailClick && onEmailClick(email)}
                  className="py-2.5 border-b border-border last:border-0 cursor-pointer hover:bg-bg-hover px-2 -mx-2 rounded"
                >
                  <div className="flex items-center gap-2 mb-0.5">
                    <Badge color={CAT_COLORS[email.category] || 'gray'}>
                      {email.category}
                    </Badge>
                    {email.urgency === 'respond' && (
                      <span className="w-2 h-2 rounded-full bg-accent-red" />
                    )}
                  </div>
                  <div className="text-sm truncate">{email.subject}</div>
                  <div className="flex items-center gap-2 mt-0.5">
                    <span className="text-xs text-text-muted">
                      {email.from_name}
                    </span>
                    <span className="text-xs text-text-muted">
                      {email.date?.split('T')[0]}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-sm text-text-muted">No emails for this client</div>
          )}
        </div>
      </div>
    </>
  )
}
