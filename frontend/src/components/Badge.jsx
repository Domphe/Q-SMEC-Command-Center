const COLOR_MAP = {
  blue: { bg: 'bg-accent-blue/10', text: 'text-accent-blue', border: 'border-accent-blue/20' },
  green: { bg: 'bg-accent-green/10', text: 'text-accent-green', border: 'border-accent-green/20' },
  amber: { bg: 'bg-accent-amber/10', text: 'text-accent-amber', border: 'border-accent-amber/20' },
  red: { bg: 'bg-accent-red/10', text: 'text-accent-red', border: 'border-accent-red/20' },
  purple: { bg: 'bg-accent-purple/10', text: 'text-accent-purple', border: 'border-accent-purple/20' },
  cyan: { bg: 'bg-accent-cyan/10', text: 'text-accent-cyan', border: 'border-accent-cyan/20' },
  gray: { bg: 'bg-text-muted/10', text: 'text-text-muted', border: 'border-text-muted/20' },
}

export default function Badge({ children, color = 'blue' }) {
  const c = COLOR_MAP[color] || COLOR_MAP.blue
  return (
    <span className={`inline-block px-2 py-0.5 rounded text-xs font-semibold font-mono border ${c.bg} ${c.text} ${c.border}`}>
      {children}
    </span>
  )
}
