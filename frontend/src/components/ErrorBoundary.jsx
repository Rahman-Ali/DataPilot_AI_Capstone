import { Component } from 'react'

export default class ErrorBoundary extends Component {
  state = { hasError: false }

  static getDerivedStateFromError() {
    return { hasError: true }
  }

  componentDidCatch(error, info) {
    console.error('DataPilot UI error:', error, info)
  }

  render() {
    if (this.state.hasError) {
      return (
        <main className="grid min-h-screen place-items-center bg-canvas px-6 text-copy">
          <section className="max-w-lg text-center">
            <p className="text-sm font-semibold tracking-[0.2em] text-mint-400 uppercase">
              Workspace protected
            </p>
            <h1 className="mt-4 text-4xl font-bold tracking-tight">
              DataPilot encountered unexpected turbulence.
            </h1>
            <p className="mt-4 text-muted">
              Your data has not been changed. Reload the workspace or return to the overview.
            </p>
            <div className="mt-8 flex justify-center gap-3">
              <button
                className="rounded-xl bg-mint-400 px-5 py-3 font-bold text-night-950 hover:bg-[#6aefd0]"
                onClick={() => window.location.reload()}
                type="button"
              >
                Reload
              </button>
              <a className="rounded-xl border border-line bg-surface px-5 py-3 font-semibold" href="/">
                Dashboard
              </a>
            </div>
          </section>
        </main>
      )
    }

    return this.props.children
  }
}
