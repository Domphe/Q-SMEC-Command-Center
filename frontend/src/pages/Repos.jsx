import { useState, useEffect } from 'react'
import { api } from '../api'
import Card from '../components/Card'
import Badge from '../components/Badge'

const HEALTH_COLORS = {
  excellent: 'green', good: 'blue', fair: 'amber',
  caution: 'amber', error: 'red', missing: 'gray',
}

const DOMAIN_COLORS = {
  ENGINE: '#ef4444', DOCS: '#3b82f6', PRODUCT: '#8b5cf6',
  SCIENCE: '#10b981', DATA: '#06b6d4', TESTING: '#f59e0b',
  OFFICE: '#64748b', INFRA: '#f97316', AI: '#8b5cf6',
}

export default function Repos() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.getRepos()
      .then(setData)
      .catch(err => console.error('Repos fetch failed:', err))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="text-text-muted">Loading repos...</div>

  const { repos = [] } = data || {}

  // Group by domain
  const domains = {}
  repos.forEach(r => {
    if (!domains[r.domain]) domains[r.domain] = []
    domains[r.domain].push(r)
  })

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-lg font-semibold">Repository Health</h1>
        <span className="font-mono text-xs text-text-muted">{repos.length} repos</span>
      </div>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-3">
        {repos.map(repo => (
          <Card key={repo.name} className="hover:border-border-active transition-colors">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <Badge color={HEALTH_COLORS[repo.health] || 'gray'}>{repo.health}</Badge>
                <span className="text-[10px] font-mono px-1.5 py-0.5 rounded"
                      style={{ color: DOMAIN_COLORS[repo.domain], backgroundColor: (DOMAIN_COLORS[repo.domain] || '#64748b') + '18' }}>
                  {repo.domain}
                </span>
              </div>
              <h3 className="font-semibold text-sm">{repo.name}</h3>
              <div className="text-xs text-text-muted mt-1">{repo.desc}</div>
              <div className="flex items-center gap-3 mt-2 text-xs text-text-muted font-mono">
                {repo.branch && <span>⎇ {repo.branch}</span>}
                {repo.commit_age && <span>{repo.commit_age}</span>}
                {repo.dirty && <span className="text-accent-amber">● dirty</span>}
              </div>
              {repo.last_commit && (
                <div className="text-xs text-text-secondary mt-1 truncate">{repo.last_commit}</div>
              )}
            </div>
          </Card>
        ))}
      </div>
    </div>
  )
}
