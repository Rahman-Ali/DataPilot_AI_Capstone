import { useParams } from 'react-router'
import PageIntro from '../../components/ui/PageIntro.jsx'

const stages = [
  { name: 'PilotFlow', detail: 'Coordinating the analysis plan', status: 'complete' },
  { name: 'DataLens', detail: 'Profiling columns and data quality', status: 'complete' },
  { name: 'CleanCraft', detail: 'Preparing the feature pipeline', status: 'active' },
  { name: 'ModelForge', detail: 'Waiting to compare candidates', status: 'waiting' },
  { name: 'InsightBoard', detail: 'Waiting to explain the result', status: 'waiting' },
]

function StatusIcon({ status }) {
  if (status === 'complete') {
    return (
      <span className="grid size-8 place-items-center rounded-full bg-mint-400 text-night-950 shadow-[0_0_16px_rgb(69_230_193/28%)]">
        <svg aria-hidden="true" className="size-4" fill="none" viewBox="0 0 20 20"><path d="m5 10 3 3 7-7" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" /></svg>
      </span>
    )
  }

  if (status === 'active') {
    return <span className="grid size-8 place-items-center rounded-full border border-electric-400/40 bg-electric-400/12"><span className="size-2.5 animate-pulse rounded-full bg-electric-400 shadow-[0_0_12px_#7c8cff]" /></span>
  }

  return <span className="grid size-8 place-items-center rounded-full border border-line bg-raised"><span className="size-2 rounded-full bg-subtle" /></span>
}

export default function RunProgressPage() {
  const { runId } = useParams()
  const progress = 42

  return (
    <>
      <PageIntro
        description={`Track analysis ${runId} as each specialized agent completes its part of the workflow.`}
        eyebrow="Run tracking"
        status="Analysis in progress"
        title="Every decision, visible as it happens."
      />

      <section className="panel-glow mt-10 overflow-hidden rounded-3xl border border-line bg-surface">
        <div className="border-b border-line p-6 sm:p-8">
          <div className="flex flex-col gap-5 sm:flex-row sm:items-end sm:justify-between">
            <div>
              <p className="text-xs font-bold tracking-[0.18em] text-electric-400 uppercase">Overall progress</p>
              <h2 className="mt-2 text-2xl font-bold text-copy">Preparing your training data</h2>
              <p className="mt-2 text-sm text-muted">CleanCraft is building a consistent, reusable preprocessing pipeline.</p>
            </div>
            <p className="font-mono text-4xl font-bold tracking-[-0.05em] text-copy">{progress}<span className="text-lg text-subtle">%</span></p>
          </div>
          <div aria-label={`${progress}% complete`} aria-valuemax="100" aria-valuemin="0" aria-valuenow={progress} className="mt-7 h-2.5 overflow-hidden rounded-full bg-raised" role="progressbar">
            <div className="relative h-full rounded-full bg-gradient-to-r from-electric-400 to-mint-400 transition-[width] duration-700" style={{ width: `${progress}%` }}>
              <span className="absolute inset-y-0 right-0 w-12 bg-white/25 blur-sm" />
            </div>
          </div>
          <div className="mt-3 flex justify-between text-[11px] font-semibold text-subtle">
            <span>Started 09:42</span>
            <span>Estimated time remaining · 3 min</span>
          </div>
        </div>

        <div className="grid lg:grid-cols-[1.15fr_0.85fr]">
          <div className="border-b border-line p-6 sm:p-8 lg:border-r lg:border-b-0">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-bold text-copy">Agent workflow</h2>
              <span className="rounded-full border border-line bg-raised px-3 py-1 text-xs font-semibold text-muted">2 of 5 complete</span>
            </div>
            <div className="relative mt-6 space-y-3">
              <span aria-hidden="true" className="absolute top-5 bottom-5 left-4 w-px bg-line" />
              {stages.map((stage, index) => (
                <article className={`relative flex items-center gap-4 rounded-2xl border p-4 transition ${stage.status === 'active' ? 'border-electric-400/35 bg-electric-400/[0.06]' : 'border-line bg-raised'}`} key={stage.name}>
                  <StatusIcon status={stage.status} />
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <h3 className="text-sm font-bold text-copy">{stage.name}</h3>
                      {stage.status === 'active' && <span className="rounded-full bg-electric-400/12 px-2 py-0.5 text-[9px] font-bold tracking-wide text-electric-400 uppercase">Working</span>}
                    </div>
                    <p className="mt-1 text-xs text-muted">{stage.detail}</p>
                  </div>
                  <span className="font-mono text-[10px] text-subtle">0{index + 1}</span>
                </article>
              ))}
            </div>
          </div>

          <aside className="p-6 sm:p-8" aria-labelledby="activity-heading">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-bold text-copy" id="activity-heading">Live activity</h2>
              <span className="flex items-center gap-2 text-[10px] font-bold tracking-wide text-mint-400 uppercase"><span className="size-1.5 animate-pulse rounded-full bg-mint-400" /> Updating</span>
            </div>
            <ol className="mt-6 space-y-6">
              {[
                ['09:44:18', 'CleanCraft', 'Encoding 3 categorical features'],
                ['09:44:06', 'CleanCraft', 'Missing-value strategy selected'],
                ['09:43:41', 'DataLens', 'Dataset profile completed'],
                ['09:42:57', 'PilotFlow', 'Analysis plan approved'],
              ].map(([time, agent, message]) => (
                <li className="grid grid-cols-[4.5rem_1fr] gap-3" key={time}>
                  <time className="font-mono text-[10px] text-subtle">{time}</time>
                  <div>
                    <p className="text-xs font-bold text-electric-400">{agent}</p>
                    <p className="mt-1 text-sm leading-5 text-muted">{message}</p>
                  </div>
                </li>
              ))}
            </ol>
          </aside>
        </div>
      </section>
    </>
  )
}
