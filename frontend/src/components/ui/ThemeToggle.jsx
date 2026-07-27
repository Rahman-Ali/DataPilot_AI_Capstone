import { useState } from 'react'

export default function ThemeToggle() {
  const [theme, setTheme] = useState(() => document.documentElement.dataset.theme || 'dark')
  const isDark = theme === 'dark'

  function toggleTheme() {
    const nextTheme = isDark ? 'light' : 'dark'
    document.documentElement.dataset.theme = nextTheme
    window.localStorage.setItem('datapilot-theme', nextTheme)
    setTheme(nextTheme)
  }

  return (
    <button
      aria-label={`Switch to ${isDark ? 'light' : 'dark'} theme`}
      className="grid size-10 shrink-0 place-items-center rounded-xl border border-line bg-surface text-muted transition hover:-translate-y-0.5 hover:text-copy"
      onClick={toggleTheme}
      title={`Switch to ${isDark ? 'light' : 'dark'} theme`}
      type="button"
    >
      {isDark ? (
        <svg aria-hidden="true" className="size-5" fill="none" viewBox="0 0 24 24">
          <circle cx="12" cy="12" r="3.5" stroke="currentColor" strokeWidth="1.7" />
          <path d="M12 2v2m0 16v2M4.93 4.93l1.42 1.42m11.3 11.3 1.42 1.42M2 12h2m16 0h2M4.93 19.07l1.42-1.42m11.3-11.3 1.42-1.42" stroke="currentColor" strokeLinecap="round" strokeWidth="1.7" />
        </svg>
      ) : (
        <svg aria-hidden="true" className="size-5" fill="none" viewBox="0 0 24 24">
          <path d="M20 15.2A8.3 8.3 0 0 1 8.8 4 8.3 8.3 0 1 0 20 15.2Z" stroke="currentColor" strokeLinejoin="round" strokeWidth="1.7" />
        </svg>
      )}
    </button>
  )
}
