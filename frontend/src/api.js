/**
 * API fetch wrapper for the Q-SMEC Command Center backend.
 */

const BASE = '/api'

async function request(path, options = {}) {
  const url = `${BASE}${path}`
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || 'API error')
  }
  return res.json()
}

export const api = {
  // Overview
  getOverview: () => request('/overview'),

  // Emails
  getEmails: (params = {}) => {
    const qs = new URLSearchParams(params).toString()
    return request(`/emails${qs ? '?' + qs : ''}`)
  },
  syncEmails: () => request('/emails/sync', { method: 'POST' }),
  categorizeEmail: (id, data) => request(`/emails/${id}/categorize`, { method: 'POST', body: JSON.stringify(data) }),
  createNoteFromEmail: (id) => request(`/emails/${id}/create-note`, { method: 'POST' }),

  // Clients
  getClients: (params = {}) => {
    const qs = new URLSearchParams(params).toString()
    return request(`/clients${qs ? '?' + qs : ''}`)
  },
  createClient: (data) => request('/clients', { method: 'POST', body: JSON.stringify(data) }),
  updateClient: (id, data) => request(`/clients/${id}`, { method: 'PUT', body: JSON.stringify(data) }),

  // Pipeline
  getPipeline: (params = {}) => {
    const qs = new URLSearchParams(params).toString()
    return request(`/pipeline${qs ? '?' + qs : ''}`)
  },
  getUCStatus: (uc) => request(`/pipeline/${uc}`),

  // Repos
  getRepos: () => request('/repos'),
  getRepoHealth: (name) => request(`/repos/${name}/health`),

  // Notes
  getNotes: (params = {}) => {
    const qs = new URLSearchParams(params).toString()
    return request(`/notes${qs ? '?' + qs : ''}`)
  },
  createNote: (data) => request('/notes', { method: 'POST', body: JSON.stringify(data) }),
  updateNote: (id, data) => request(`/notes/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteNote: (id) => request(`/notes/${id}`, { method: 'DELETE' }),
  routeNote: (id) => request(`/notes/${id}/route`, { method: 'POST' }),
  exportNotes: () => request('/notes/export', { method: 'POST' }),

  // AI Router
  routeTask: (data) => request('/ai/route', { method: 'POST', body: JSON.stringify(data) }),
  executeTask: (data) => request('/ai/execute', { method: 'POST', body: JSON.stringify(data) }),

  // Health
  health: () => request('/health'),
}
