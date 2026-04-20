import { useState, useEffect } from 'react'
import { api } from '../api'
import Card from '../components/Card'
import Badge from '../components/Badge'

const STATUS_COLORS = { active: 'green', prospect: 'amber', early: 'cyan', inactive: 'gray' }
const PRIORITY_COLORS = { high: 'red', medium: 'amber', low: 'gray' }
const TYPE_LABELS = { client: 'Client', partner: 'Partner', research: 'Research' }

export default function Clients() {
  const [data, setData] = useState(null)
  const [filter, setFilter] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const params = {}
    if (filter) params.status = filter
    api.getClients(params)
      .then(setData)
      .catch(err => console.error('Clients fetch failed:', err))
      .finally(() => setLoading(false))
  }, [filter])

  if (loading) return <div className="text-text-muted">Loading clients...</div>

  const { clients = [] } = data || {}

  // Group by status
  const groups = {}
  clients.forEach(c => {
    const key = c.status || 'unknown'
    if (!groups[key]) groups[key] = []
    groups[key].push(c)
  })

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-semibold">Clients & Partners</h1>
        <span className="font-mono text-xs text-text-muted">{clients.length} total</span>
      </div>

      {/* Status filters */}
      <div className="flex flex-wrap gap-2">
        {['active', 'prospect', 'early'].map(status => (
          <button
            key={status}
            onClick={() => setFilter(filter === status ? null : status)}
            className={`px-3 py-1 text-xs rounded border capitalize ${filter === status ? 'border-accent-blue text-accent-blue bg-accent-blue/10' : 'border-border text-text-muted hover:text-text-primary'}`}
          >
            {status} ({(groups[status] || []).length})
          </button>
        ))}
      </div>

      {/* Client cards */}
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-3">
        {clients.map(client => (
          <Card key={client.id} className="hover:border-border-active transition-colors">
            <div>
              <div className="flex items-center gap-2 mb-2">
                <Badge color={STATUS_COLORS[client.status] || 'gray'}>{client.status}</Badge>
                <Badge color={PRIORITY_COLORS[client.priority] || 'gray'}>{client.priority}</Badge>
                <span className="text-xs text-text-muted">{TYPE_LABELS[client.type] || client.type}</span>
              </div>
              <h3 className="font-semibold text-sm">{client.name}</h3>
              <div className="text-xs text-text-muted mt-1">{client.sector}</div>
              {client.contact && <div className="text-xs text-text-secondary mt-1">Contact: {client.contact}</div>}
              {client.uc && client.uc.length > 0 && (
                <div className="flex flex-wrap gap-1 mt-2">
                  {client.uc.map(uc => <Badge key={uc} color="purple">{uc}</Badge>)}
                </div>
              )}
              <div className="flex items-center gap-3 mt-2 text-xs text-text-muted">
                {client.nda_status && <span>NDA: {client.nda_status}</span>}
                {client.data_size && <span>{client.data_size}</span>}
              </div>
              {client.notes && <div className="text-xs text-text-secondary mt-2 line-clamp-2">{client.notes}</div>}
              {client.last_touch && (
                <div className="text-[10px] text-text-muted mt-2">Last touch: {client.last_touch}</div>
              )}
            </div>
          </Card>
        ))}
      </div>
    </div>
  )
}
