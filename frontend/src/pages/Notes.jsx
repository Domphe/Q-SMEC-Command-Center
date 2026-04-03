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
      alert(`Exported ${result.exported} notes to bridge`)
    } catch (err) {
      console.error('Export failed:', err)
    }
  }

  if (loading) return <div className="text-text-muted">Loading notes...</div>

  const { notes = [] } = data || {}

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-semibold">Notes</h1>
        <button
          onClick={handleExport}
          className="px-3 py-1.5 bg-accent-green/20 text-accent-green text-xs rounded hover:bg-accent-green/30"
        >
          Export to Bridge
        </button>
      </div>

      {/* Create note */}
      <Card title="New Note" icon="✏️">
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
      <Card title="All Notes" icon="📝" count={notes.length}>
        <div className="space-y-0">
          {notes.map(note => (
            <div key={note.id} className="flex items-start gap-3 py-3 border-b border-border last:border-0">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <Badge color={TAG_COLORS[note.tag] || 'gray'}>{note.tag}</Badge>
                  {note.status !== 'note' && <Badge color={note.status === 'done' ? 'green' : 'amber'}>{note.status}</Badge>}
                  {note.target_tool && <span className="text-[10px] text-text-muted font-mono">→ {note.target_tool}</span>}
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
                  ×
                </button>
              </div>
            </div>
          ))}
          {notes.length === 0 && <div className="text-sm text-text-muted py-4 text-center">No notes yet — create one above</div>}
        </div>
      </Card>
    </div>
  )
}
