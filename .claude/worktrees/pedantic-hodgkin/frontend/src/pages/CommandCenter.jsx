import { useState } from 'react'
import { api } from '../api'
import Card from '../components/Card'
import Badge from '../components/Badge'

const TOOLS = [
  { name: 'Claude Code', icon: '⌨️', desc: 'Terminal: git, scripts, DB, CI/CD, pipeline execution',
    strengths: 'Git ops, script execution, database queries, CI debugging' },
  { name: 'Claude Cowork', icon: '📄', desc: 'Filesystem: bulk file ops, docs, cross-repo edits',
    strengths: 'Multi-file edits, document generation, cross-repo refactors' },
  { name: 'Claude Project', icon: '🌐', desc: 'Research: web search, planning, strategy, analysis',
    strengths: 'Research synthesis, strategic planning, spec writing' },
]

const MODEL_GUIDE = [
  { model: 'Sonnet', range: '0-65', desc: 'Fast, efficient — routine tasks, single-file edits, categorization' },
  { model: 'Opus', range: '66-100', desc: 'Deep reasoning — multi-repo architecture, physics, strategy' },
  { model: 'Gemini', range: 'Cross-val', desc: 'Second opinion — validation, verification, cross-checking' },
]

export default function CommandCenter() {
  const [taskInput, setTaskInput] = useState('')
  const [routeResult, setRouteResult] = useState(null)
  const [routing, setRouting] = useState(false)

  const handleRoute = async () => {
    if (!taskInput.trim()) return
    setRouting(true)
    try {
      const result = await api.routeTask({ task_description: taskInput })
      setRouteResult(result)
    } catch (err) {
      console.error('Route failed:', err)
    } finally {
      setRouting(false)
    }
  }

  return (
    <div className="space-y-4">
      <h1 className="text-lg font-semibold">Command Center</h1>

      {/* AI Task Router */}
      <Card title="AI Task Router" icon="🎯">
        <div className="space-y-3">
          <textarea
            value={taskInput}
            onChange={e => setTaskInput(e.target.value)}
            placeholder="Describe a task... I'll recommend the best model and tool"
            className="w-full bg-bg-secondary border border-border rounded p-3 text-sm resize-none h-20 text-text-primary placeholder:text-text-muted"
          />
          <button
            onClick={handleRoute}
            disabled={routing}
            className="px-4 py-2 bg-accent-blue text-white text-sm rounded font-medium hover:bg-accent-blue/80 disabled:opacity-50"
          >
            {routing ? 'Analyzing...' : 'Route Task'}
          </button>

          {routeResult && (
            <div className="bg-bg-secondary border border-border rounded p-4 space-y-2">
              <div className="flex items-center gap-3">
                <span className="text-sm">Recommended:</span>
                <Badge color={routeResult.recommended_model === 'opus' ? 'purple' : 'blue'}>
                  {routeResult.recommended_model}
                </Badge>
                {routeResult.tool && (
                  <Badge color="cyan">→ {routeResult.tool}</Badge>
                )}
              </div>
              <div className="flex items-center gap-4 text-xs text-text-muted font-mono">
                <span>Complexity: {routeResult.complexity_score}/100</span>
                <span>Confidence: {Math.round((routeResult.confidence || 0) * 100)}%</span>
                <span>~{routeResult.estimated_tokens} tokens</span>
              </div>
              <div className="text-xs text-text-secondary">{routeResult.reasoning}</div>
              {routeResult.alternate && (
                <div className="text-xs text-text-muted">Fallback: {routeResult.alternate}</div>
              )}
            </div>
          )}
        </div>
      </Card>

      {/* Tool Cards */}
      <div className="grid md:grid-cols-3 gap-3">
        {TOOLS.map(tool => (
          <Card key={tool.name} title={tool.name} icon={tool.icon}>
            <div className="text-xs text-text-secondary">{tool.desc}</div>
            <div className="text-xs text-text-muted mt-1">
              <span className="font-semibold text-text-secondary">Best for:</span> {tool.strengths}
            </div>
          </Card>
        ))}
      </div>

      {/* Model Selection Guide */}
      <Card title="Model Selection Guide" icon="🧠">
        <div className="space-y-2">
          {MODEL_GUIDE.map(m => (
            <div key={m.model} className="flex items-center gap-3 py-2 border-b border-border last:border-0">
              <Badge color={m.model === 'Opus' ? 'purple' : m.model === 'Gemini' ? 'green' : 'blue'}>
                {m.model}
              </Badge>
              <span className="font-mono text-xs text-text-muted w-16 shrink-0">{m.range}</span>
              <span className="text-xs text-text-secondary">{m.desc}</span>
            </div>
          ))}
        </div>
      </Card>

      {/* Quick Reference */}
      <Card title="Quick Reference" icon="📋">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
          <div className="bg-bg-secondary rounded p-2">
            <div className="font-semibold text-accent-blue">18</div>
            <div className="text-text-muted">Repositories</div>
          </div>
          <div className="bg-bg-secondary rounded p-2">
            <div className="font-semibold text-accent-purple">23</div>
            <div className="text-text-muted">Use Cases</div>
          </div>
          <div className="bg-bg-secondary rounded p-2">
            <div className="font-semibold text-accent-red">32</div>
            <div className="text-text-muted">Elements</div>
          </div>
          <div className="bg-bg-secondary rounded p-2">
            <div className="font-semibold text-accent-green">5</div>
            <div className="text-text-muted">UC Categories</div>
          </div>
        </div>
      </Card>
    </div>
  )
}
