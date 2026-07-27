import { Link } from 'react-router'

export default function NotFoundPage() {
  return (
    <section className="grid min-h-[58vh] place-items-center text-center">
      <div className="relative max-w-xl">
        <div aria-hidden="true" className="absolute top-1/2 left-1/2 size-56 -translate-x-1/2 -translate-y-1/2 rounded-full bg-electric-400/12 blur-3xl" />
        <div className="relative">
          <p className="font-mono text-xs font-bold tracking-[0.3em] text-mint-400">ERROR / 404</p>
          <h1 className="text-gradient mt-6 text-5xl font-bold tracking-[-0.05em] sm:text-6xl">This flight path ends here.</h1>
          <p className="mx-auto mt-5 max-w-lg text-base leading-7 text-muted">The destination may have moved or the address is incomplete. Your workspace and data remain safe.</p>
          <Link className="mt-8 inline-flex rounded-xl bg-mint-400 px-5 py-3 font-bold text-night-950 transition hover:bg-[#6aefd0]" to="/">Return to workspace</Link>
        </div>
      </div>
    </section>
  )
}
