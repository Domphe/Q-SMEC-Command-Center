import { useState, useEffect, useCallback } from 'react'
import { api } from '../api'
import Card from '../components/Card'
import Badge from '../components/Badge'

const TAG_OPTIONS = ['general', 'action', 'research', 'client', 'pipeline', 'idea']
const TAG_COLORS = {
  general: 'gray', action: 'red', research: 'blue',
  client: 'green', pipeline: 'purple', idea: 'cyan',
}

export default function Notes() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [newText, setNewText] = useState('')
  const [newTag, setNewTag] = useState('general')
  const [pickerOpen, setPickerOpen] = useState(false)
  const [pickerEmails, setPickerEmails] = useState([])
  const [pickerSearch, setPickerSearch] = useState('')
  const [pickerLoading, setPickerLoading] = useState(false)

  const loadNotes = useCallback(() => {
    api.getNotes()
      .then(setData)
      .catch(err => console.error('Notes fetch failed:', err))
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => { loadNotes() }, [loadNotes])

  const handleCreate = async () => {
    if (!newText.trim()) return
    try {
      await api.createNote({ text: newText, tag: newTag })
      setNewText('')
      loadNotes()
    } catch (err) {
      console.error('Create note failed:', err)
    }
  }

  const handleDelete = async (id) => {
    try {
      await api.deleteNote(id)
      loadNotes()
    } catch (err) {
      console.error('Delete note failed:', err)
    }
  }

  const handleRoute = async (id) => {
    try {
      await api.routeNote(id)
      loadNotes()
    } catch (err) {
      console.error('Route note failed:', err)
    }
  }

  const handleExport = async () => {
    try {
      const result = await api.exportNotes()
      alert('Exported ' + (result.exported || 0) + ' notes to bridge')
    } catch (err) {
      console.error('Export failed:', err)
    }
  }

  const openEmailPicker = async () => {
    setPickerOpen(true)
    setPickerLoading(true)
    try {
      const res = await api.getEmails({ limit: 20 })
      setPickerEmails(res.emails || [])
    } catch (err) {
      console.error('Email picker fetch failed:', err)
    } finally {
      setPickerLoading(false)
    }
  }

  const handlePickEmail = async (emailId) => {
    try {
      await api.createNoteFromEmail(emailId)
      setPickerOpen(false)
      setPickerSearch('')
      loadNotes()
    } catch (err) {
      console.error('Create note from email failed:', err)
    }
  }

  const filteredPickerEmails = pickerSearch
    ? pickerEmails.filter(e =>
        (e.subject || '').toLowerCase().includes(pickerSearch.toLowerCase()) ||
        (e.from_name || '').toLowerCase().includes(pickerSearch.toLowerCase())
      )
    : pickerEmails

  if (loading) return <div className="text-text-muted">Loading notes...</div>

  const { notes = [] } = data || {}

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-semibold">Notes</h1>
        <div className="flex gap-2">
          <button
            onClick={openEmailPicker}
            className="px-3 py-1.5 bg-accent-blue/20 text-accent-blue text-xs rounded hover:bg-accent-blue/30"
          >
            + From Email
          </button>
          <button
            onClick={handleExport}
            className="px-3 py-1.5 bg-accent-green/20 text-accent-green text-xs rounded hover:bg-accent-green/30"
          >
            Export to Bridge
          </button>
        </div>
      </div>

      {/* Create note */}
      <Card title="New Note" icon="&#9999;">
        <div className="space-y-3">
          <textarea
            value={newText}
            onChange={e => setNewText(e.target.value)}
            placeholder="Type a note... tag it, route it to an AI tool"
            className="w-full bg-bg-secondary border border-border rounded p-3 text-sm resize-none h-20 text-text-primary placeholder:text-text-muted"
          />
          <div className="flex items-center gap-3">
            <select
              value={newTag}
              onChange={e => setNewTag(e.target.value)}
              className="bg-bg-secondary border border-border rounded px-2 py-1 text-xs text-text-primary"
            >
              {TAG_OPTIONS.map(t => <option key={t} value={t}>{t}</option>)}
            </select>
            <button
              onClick={handleCreate}
              className="px-4 py-1.5 bg-accent-blue text-white text-xs rounded font-medium hover:bg-accent-blue/80"
            >
              Add Note
            </button>
          </div>
        </div>
      </Card>

      {/* Notes list */}
      <Card title="All Notes" icon="&#128221;" count={notes.length}>
        <div className="space-y-0">
          {notes.map(note => (
            <div key={note.id} className="flex items-start gap-3 py-3 border-b border-border last:border-0">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <Badge color={TAG_COLORS[note.tag] || 'gray'}>{note.tag}</Badge>
                  {note.status !== 'note' && <Badge color={note.status === 'done' ? 'green' : 'amber'}>{note.status}</Badge>}
                  {note.target_tool && <span className="text-[10px] text-text-muted font-mono">&rarr; {note.target_tool}</span>}
                </div>
                <div className="text-sm">{note.text}</div>
                <div className="text-[10px] text-text-muted mt-1">
                  {note.created_at?.split('T')[0]}
                </div>
              </div>
              <div className="flex gap-1 shrink-0">
                <button
                  onClick={() => handleRoute(note.id)}
                  className="px-2 py-1 text-[10px] bg-accent-purple/20 text-accent-purple rounded hover:bg-accent-purple/30"
                  title="Route to AI tool"
                >
                  Route
                </button>
                <button
                  onClick={() => handleDelete(note.id)}
                  className="px-2 py-1 text-[10px] bg-accent-red/20 text-accent-red rounded hover:bg-accent-red/30"
                  title="Delete"
                >
                  &times;
                </button>
              </div>
            </div>
          ))}
          {notes.length === 0 && <div className="text-sm text-text-muted py-4 text-center">No notes yet &mdash; create one above</div>}
        </div>
      </Card>

      {/* Email picker modal */}
      {pickerOpen && (
        <>
          <div
            className="fixed inset-0 bg-black/40 z-40"
            onClick={() => { setPickerOpen(false); setPickerSearch('') }}
          />
          <div className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-md bg-bg-secondary border border-border rounded-lg shadow-2xl z-50 max-h-[70vh] flex flex-col">
            <div className="flex items-center justify-between px-4 py-3 border-b border-border shrink-0">
              <span className="text-sm font-semibold">Create Note from Email</span>
              <button
                onClick={() => { setPickerOpen(false); setPickerSearch('') }}
                className="text-text-muted hover:text-text-primary text-lg"
              >
                &times;
              </button>
            </div>
            <div className="px-4 py-2 border-b border-border shrink-0">
              <input
                type="text"
                value={pickerSearch}
                onChange={e => setPickerSearch(e.target.value)}
                placeholder="Search emails..."
                className="w-full bg-bg-primary border border-border rounded px-3 py-1.5 text-sm text-text-primary placeholder:text-text-muted"
                autoFocus
              />
            </div>
            <div className="flex-1 overflow-y-auto p-2">
              {pickerLoading ? (
                <div className="text-sm text-text-muted p-4 text-center">Loading...</div>
              ) : filteredPickerEmails.length > 0 ? (
                filteredPickerEmails.map(email => (
                  <button
                    key={email.id}
                    onClick={() => handlePickEmail(email.id)}
                    className="w-full text-left px-3 py-2 hover:bg-bg-hover rounded"
                  >
                    <div className="text-sm truncate">{email.subject}</div>
                    <div className="text-xs text-text-muted">
                      {email.from_name} &middot; {email.date?.split('T')[0]}
                    </div>
                  </button>
                ))
              ) : (
                <div className="text-sm text-text-muted p-4 text-center">No emails found</div>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  )
}
