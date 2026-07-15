import { NavLink } from 'react-router'
import ThemeToggle from '../ui/ThemeToggle.jsx'

const links = [
  { label: 'Workspace', to: '/', end: true },
  { label: 'Datasets', to: '/upload' },
  { label: 'Live run', to: '/runs/demo-run/progress' },
  { label: 'Insights', to: '/runs/demo-run/results' },
]

function BrandMark() {
  return (
    <span className="relative grid size-10 place-items-center overflow-hidden rounded-xl border border-line bg-surface shadow-[0_0_30px_rgb(124_140_255/18%)]">
      <span className="absolute inset-0 bg-gradient-to-br from-electric-400/30 to-mint-400/10" />
      <svg aria-hidden="true" className="relative size-6" fill="none" viewBox="0 0 24 24">
        <circle cx="6" cy="12" fill="#45e6c1" r="2" />
        <circle cx="18" cy="6" fill="#9ca8ff" r="2" />
        <circle cx="18" cy="18" fill="#ffffff" r="2" />
        <path d="m8 11 8-4M8 13l8 4" stroke="currentColor" strokeWidth="1.5" />
      </svg>
    </span>
  )
}

export default function Navigation() {
  return (
    <header className="sticky top-0 z-40 border-b border-line bg-canvas/90 backdrop-blur-xl transition-colors duration-300">
      <div className="mx-auto flex max-w-[1440px] items-center justify-between gap-6 px-5 py-4 sm:px-8 lg:px-12">
        <NavLink aria-label="DataPilot AI workspace" className="flex shrink-0 items-center gap-3" to="/">
          <BrandMark />
          <span>
            <span className="block text-base font-bold tracking-[-0.03em] text-copy">DataPilot</span>
            <span className="block text-[10px] font-semibold tracking-[0.22em] text-mint-400 uppercase">AI workspace</span>
          </span>
        </NavLink>
        <nav aria-label="Primary navigation" className="hidden items-center rounded-xl border border-line bg-surface p-1 md:flex">
          {links.map((link) => (
            <NavLink
              className={({ isActive }) => `rounded-lg px-4 py-2 text-sm font-medium transition-all ${isActive ? 'bg-raised text-copy shadow-sm' : 'text-muted hover:bg-raised hover:text-copy'}`}
              end={link.end}
              key={link.to}
              to={link.to}
            >
              {link.label}
            </NavLink>
          ))}
        </nav>
        <div className="flex items-center gap-3">
          <span className="hidden items-center gap-2 text-xs font-medium text-muted xl:flex">
            <span className="size-1.5 rounded-full bg-mint-400 shadow-[0_0_8px_#45e6c1]" /> System ready
          </span>
          <ThemeToggle />
          <NavLink className="hidden rounded-xl bg-action px-4 py-2.5 text-sm font-bold text-action-copy transition hover:bg-mint-400 hover:text-night-950 sm:block" to="/upload">New analysis</NavLink>
        </div>
      </div>
      <nav aria-label="Mobile navigation" className="flex gap-1 overflow-x-auto border-t border-line px-4 py-2 md:hidden">
        {links.map((link) => (
          <NavLink className={({ isActive }) => `shrink-0 rounded-lg px-3 py-2 text-xs font-semibold ${isActive ? 'bg-raised text-copy' : 'text-subtle'}`} end={link.end} key={link.to} to={link.to}>
            {link.label}
          </NavLink>
        ))}
      </nav>
    </header>
  )
}
