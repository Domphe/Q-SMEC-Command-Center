export default function KPICard({ label, value, sub, color = '#3b82f6' }) {
  return (
    <div
      className="bg-bg-card border border-border rounded-lg px-4 py-3.5 min-w-[140px]"
      style={{ borderLeft: `3px solid ${color}` }}
    >
      <div className="font-mono text-2xl font-bold leading-none" style={{ color }}>{value}</div>
      <div className="text-xs text-text-secondary mt-1 font-medium">{label}</div>
      {sub && <div className="text-[10px] text-text-muted mt-0.5">{sub}</div>}
    </div>
  )
}
