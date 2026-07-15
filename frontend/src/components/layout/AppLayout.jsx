import { Outlet } from 'react-router'
import Navigation from './Navigation.jsx'

export default function AppLayout() {
  return (
    <div className="relative min-h-screen overflow-x-clip bg-canvas text-copy transition-colors duration-300">
      <div aria-hidden="true" className="data-grid pointer-events-none absolute inset-0 opacity-60" />
      <div aria-hidden="true" className="pointer-events-none absolute top-36 -left-28 size-80 rounded-full bg-indigo-500/10 blur-3xl" />
      <a className="fixed top-3 left-3 z-50 -translate-y-20 rounded-xl bg-action px-4 py-2 text-sm font-bold text-action-copy transition-transform focus:translate-y-0" href="#main-content">
        Skip to content
      </a>
      <Navigation />
      <main id="main-content" className="relative z-10 mx-auto w-full max-w-[1440px] px-5 py-10 sm:px-8 lg:px-12 lg:py-16">
        <Outlet />
      </main>
      <footer className="relative z-10 mx-auto flex w-full max-w-[1440px] flex-col gap-3 border-t border-line px-5 py-7 text-sm text-subtle sm:flex-row sm:items-center sm:justify-between sm:px-8 lg:px-12">
        <div className="flex items-center gap-2.5">
          <span className="size-1.5 rounded-full bg-mint-400 shadow-[0_0_10px_#45e6c1]" />
          <span>DataPilot AI</span><span className="text-line">/</span><span>Intelligent AutoML workspace</span>
        </div>
        <p>Built for transparent, human-guided decisions</p>
      </footer>
    </div>
  )
}
