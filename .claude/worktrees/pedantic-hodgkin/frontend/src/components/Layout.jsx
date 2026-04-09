import { NavLink } from 'react-router-dom'

const NAV_ITEMS = [
  { path: '/', label: 'Overview', icon: '📊' },
  { path: '/emails', label: 'Email Triage', icon: '📧' },
  { path: '/clients', label: 'Clients', icon: '🤝' },
  { path: '/pipeline', label: 'Pipeline', icon: '🔬' },
  { path: '/repos', label: 'Repos', icon: '📦' },
  { path: '/notes', label: 'Notes', icon: '📝' },
  { path: '/command-center', label: 'Cmd Center', icon: '🎯' },
]

export default function Layout({ children }) {
  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="bg-bg-secondary border-b border-border px-4 py-3 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-3">
          <span className="text-accent-blue font-bold text-lg font-mono">[Q]</span>
          <span className="font-semibold text-sm tracking-wide">Q-SMEC COMMAND CENTER</span>
        </div>
        <div className="flex items-center gap-4 text-xs text-text-muted font-mono">
          <span>v2.0</span>
          <span>18 repos</span>
          <span>23 UCs</span>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar — hidden on mobile, shown as bottom nav */}
        <nav className="hidden md:flex flex-col w-48 bg-bg-secondary border-r border-border shrink-0 py-2">
          {NAV_ITEMS.map(item => (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.path === '/'}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-2.5 text-sm transition-colors ${
                  isActive
                    ? 'bg-bg-hover text-accent-blue border-r-2 border-accent-blue'
                    : 'text-text-secondary hover:text-text-primary hover:bg-bg-hover'
                }`
              }
            >
              <span>{item.icon}</span>
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>

        {/* Main content */}
        <main className="flex-1 overflow-y-auto p-4 md:p-6">
          {children}
        </main>
      </div>

      {/* Mobile bottom nav */}
      <nav className="md:hidden flex bg-bg-secondary border-t border-border">
        {NAV_ITEMS.slice(0, 5).map(item => (
          <NavLink
            key={item.path}
            to={item.path}
            end={item.path === '/'}
            className={({ isActive }) =>
              `flex-1 flex flex-col items-center py-2 text-xs ${
                isActive ? 'text-accent-blue' : 'text-text-muted'
              }`
            }
          >
            <span className="text-lg">{item.icon}</span>
            <span>{item.label.split(' ')[0]}</span>
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <footer className="hidden md:block bg-bg-secondary border-t border-border px-4 py-2 text-xs text-text-muted font-mono text-center">
        v2.0 · NIKET-HV-01 · 18 repos · 23 UCs · 32 elements
      </footer>
    </div>
  )
}
