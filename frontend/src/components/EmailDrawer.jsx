import { useState, useEffect } from 'react'
import { api } from '../api'
import Badge from './Badge'

const CAT_COLORS = {
  research: 'blue', client: 'green', opportunity: 'amber',
  business: 'purple', noise: 'gray', pipeline: 'cyan',
  administrative: 'gray', personal: 'gray',
}

const CATEGORIES = [
  'opportunity', 'client', 'research', 'pipeline',
  'administrative', 'personal', 'business', 'noise',
]

export default function EmailDrawer({ email, onClose, onUpdate }) {
  const [recatOpen, setRecatOpen] = useState(false)
  const [toast, setToast] = useState(null)

  // Close on Escape
  useEffect(() => {
    const handler = (e) => { if (e.key === 'Escape') onClose() }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [onClose])

  if (!email) return null

  const showToast = (msg) => {
    setToast(msg)
    setTimeout(() => setToast(null), 2500)
  }

  const handleCreateNote = async () => {
    try {
      await api.createNoteFromEmail(email.id)
      showToast('Note created')
    } catch (err) {
      showToast('Failed: ' + err.message)
    }
  }

  const handleRecategorize = async (category) => {
    try {
      const updated = await api.categorizeEmail(email.id, {
        category, categorized_by: 'manual',
      })
      setRecatOpen(false)
      if (onUpdate) onUpdate(updated)
      showToast('Category updated')
    } catch (err) {
      showToast('Failed: ' + err.message)
    }
  }

  const handleMarkDone = async () => {
    try {
      const updated = await api.patchEmail(email.id, {
        action_required: false,
      })
      if (onUpdate) onUpdate(updated)
      showToast('Marked done')
    } catch (err) {
      showToast('Failed: ' + err.message)
    }
  }

  const gmailUrl = 'https://mail.google.com/mail/u/0/#inbox/' + email.id

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/40 z-40"
        onClick={onClose}
      />

      {/* Drawer panel */}
      <div className="fixed top-0 right-0 h-full w-full md:w-96 bg-bg-secondary border-l border-border z-50 flex flex-col shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-border shrink-0">
          <span className="text-sm font-semibold truncate">Email Detail</span>
          <button
            onClick={onClose}
            className="text-text-muted hover:text-text-primary text-lg leading-none"
          >
            &times;
          </button>
        </div>

        {/* Body — scrollable */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {/* Sender */}
          <div>
            <div className="text-base font-semibold">{email.from_name}</div>
            <div className="text-xs text-text-muted">{email.from_addr}</div>
          </div>

          {/* Subject */}
          <div className="text-sm font-medium">{email.subject}</div>

          {/* Date + badges */}
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-xs text-text-muted">
              {email.date ? new Date(email.date).toLocaleString() : ''}
            </span>
            <Badge color={CAT_COLORS[email.category] || 'gray'}>
              {email.category}
            </Badge>
            {email.urgency === 'respond' && (
              <span className="text-xs px-1.5 py-0.5 rounded bg-red-500/20 text-red-400 border border-red-500/30">
                Respond
              </span>
            )}
            {email.urgency === 'review' && (
              <span className="text-xs px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-400 border border-amber-500/30">
                Review
              </span>
            )}
            {email.urgency === 'archive' && (
              <span className="text-xs px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-400 border border-blue-500/30">
                Archive
              </span>
            )}
          </div>

          {/* Snippet / body */}
          <div className="bg-bg-primary rounded p-3 text-sm text-text-secondary whitespace-pre-wrap max-h-64 overflow-y-auto font-mono leading-relaxed">
            {email.snippet || 'No preview available.'}
          </div>

          {/* UC / Client badges */}
          {(email.uc || email.client) && (
            <div className="flex flex-wrap gap-2">
              {email.uc && <Badge color="purple">{email.uc}</Badge>}
              {email.client && <Badge color="cyan">{email.client}</Badge>}
              {email.has_attachment && (
                <span className="text-xs text-text-muted">Attachment</span>
              )}
            </div>
          )}
        </div>

        {/* Actions — fixed bottom */}
        <div className="border-t border-border px-4 py-3 space-y-2 shrink-0">
          {/* Primary */}
          <a
            href={gmailUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="block w-full text-center px-3 py-2 bg-accent-blue text-white text-sm rounded hover:bg-accent-blue/80"
          >
            Open in Gmail
          </a>

          {/* Secondary row */}
          <div className="flex gap-2">
            <button
              onClick={handleCreateNote}
              className="flex-1 px-3 py-1.5 bg-bg-hover text-text-primary text-xs rounded border border-border hover:border-accent-blue"
            >
              Create Note
            </button>

            <div className="flex-1 relative">
              <button
                onClick={() => setRecatOpen(!recatOpen)}
                className="w-full px-3 py-1.5 bg-bg-hover text-text-primary text-xs rounded border border-border hover:border-accent-blue"
              >
                Re-categorize
              </button>
              {recatOpen && (
                <div className="absolute bottom-full left-0 mb-1 w-full bg-bg-secondary border border-border rounded shadow-lg z-10">
                  {CATEGORIES.map((cat) => (
                    <button
                      key={cat}
                      onClick={() => handleRecategorize(cat)}
                      className="block w-full text-left px-3 py-1.5 text-xs hover:bg-bg-hover text-text-secondary hover:text-text-primary"
                    >
                      {cat}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Mark Done */}
          {email.action_required && (
            <button
              onClick={handleMarkDone}
              className="w-full px-3 py-1.5 text-xs text-text-muted hover:text-accent-green border border-border rounded hover:border-accent-green"
            >
              Mark Done
            </button>
          )}
        </div>

        {/* Toast */}
        {toast && (
          <div className="absolute bottom-20 left-1/2 -translate-x-1/2 px-4 py-2 bg-accent-green/90 text-white text-xs rounded shadow-lg">
            {toast}
          </div>
        )}
      </div>
    </>
  )
}
