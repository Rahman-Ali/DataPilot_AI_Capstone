export default function PlaceholderPanel({ title, description, steps = [] }) {
  return (
    <section className="panel-glow mt-10 overflow-hidden rounded-3xl border border-line bg-surface backdrop-blur-sm">
      <div className="flex flex-col gap-4 border-b border-line px-6 py-6 sm:flex-row sm:items-end sm:justify-between lg:px-8">
        <div>
          <p className="text-[11px] font-bold tracking-[0.18em] text-electric-400 uppercase">Workflow preview</p>
          <h2 className="mt-2 text-xl font-bold tracking-tight text-copy">{title}</h2>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-muted">{description}</p>
        </div>
        <span className="shrink-0 rounded-full border border-line bg-raised px-3 py-1.5 text-xs font-semibold text-muted">{steps.length} stages</span>
      </div>
      <div className="grid gap-px bg-line lg:grid-cols-3">
        {steps.map((step, index) => (
          <article className="group relative bg-surface p-6 transition hover:bg-raised lg:p-8" key={step.title}>
            <div className="flex items-center justify-between">
              <span className="font-mono text-xs font-bold text-mint-400">0{index + 1}</span>
              <span className="size-2 rounded-full border border-subtle transition group-hover:border-mint-400 group-hover:bg-mint-400 group-hover:shadow-[0_0_12px_#45e6c1]" />
            </div>
            <h3 className="mt-10 text-lg font-bold text-copy">{step.title}</h3>
            <p className="mt-2 text-sm leading-6 text-muted">{step.description}</p>
          </article>
        ))}
      </div>
    </section>
  )
}
