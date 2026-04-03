export default function ProgressBar({ value = 0, color = '#3b82f6', height = 6 }) {
  return (
    <div className="w-full bg-bg-secondary rounded-full overflow-hidden" style={{ height }}>
      <div
        className="h-full rounded-full transition-all duration-300"
        style={{ width: `${Math.min(100, Math.max(0, value))}%`, backgroundColor: color }}
      />
    </div>
  )
}
