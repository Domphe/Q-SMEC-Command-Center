export default function Card({ title, icon, count, headerRight, children, className = '' }) {
  return (
    <div className={`bg-bg-card border border-border rounded-lg p-4 flex flex-col gap-3 ${className}`}>
      <div className="flex justify-between items-center">
        <div className="flex items-center gap-2">
          {icon && <span className="text-sm">{icon}</span>}
          <span className="text-sm font-semibold text-text-primary tracking-wide">{title}</span>
        </div>
        <div className="flex items-center gap-2">
          {headerRight}
          {count !== undefined && (
            <span className="font-mono text-xs text-text-muted bg-bg-secondary px-2 py-0.5 rounded">
              {count}
            </span>
          )}
        </div>
      </div>
      {children}
    </div>
  )
}
