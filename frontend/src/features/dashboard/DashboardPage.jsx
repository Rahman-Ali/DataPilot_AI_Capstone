import { Link } from 'react-router'

const agents = [
  { name: 'PilotFlow', role: 'Orchestrates the full mission', color: 'bg-electric-400' },
  { name: 'DataLens', role: 'Profiles your dataset', color: 'bg-cyan-400' },
  { name: 'CleanCraft', role: 'Prepares every feature', color: 'bg-violet-400' },
  { name: 'ModelForge', role: 'Finds the best model', color: 'bg-mint-400' },
  { name: 'InsightBoard', role: 'Explains the outcome', color: 'bg-amber-300' },
]

function ArrowIcon() {
  return (
    <svg aria-hidden="true" className="size-4" fill="none" viewBox="0 0 20 20">
      <path d="M4 10h12m-5-5 5 5-5 5" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.8" />
    </svg>
  )
}

function WorkflowPreview() {
  return (
    <div className="panel-glow relative overflow-hidden rounded-[2rem] border border-line bg-surface p-4 backdrop-blur-sm sm:p-5">
      <div className="absolute inset-x-20 top-0 h-px bg-gradient-to-r from-transparent via-mint-400/80 to-transparent" />
      <div className="rounded-2xl border border-line bg-canvas p-5">
        <div className="flex items-center justify-between gap-4 border-b border-line pb-4">
          <div className="flex items-center gap-3">
            <div className="grid size-9 place-items-center rounded-xl bg-electric-400/12 text-electric-400">
              <svg aria-hidden="true" className="size-5" fill="none" viewBox="0 0 24 24">
                <path d="M7 3h7l5 5v13H7V3Z" stroke="currentColor" strokeLinejoin="round" strokeWidth="1.5" />
                <path d="M14 3v6h5M10 14h6m-6 3h4" stroke="currentColor" strokeLinecap="round" strokeWidth="1.5" />
              </svg>
            </div>
            <div>
              <p className="text-sm font-bold text-copy">customer_churn.csv</p>
              <p className="mt-0.5 text-xs text-subtle">Dataset ready for analysis</p>
            </div>
          </div>
          <span className="rounded-full bg-mint-400/10 px-2.5 py-1 text-[10px] font-bold tracking-wide text-mint-400 uppercase">Ready</span>
        </div>

        <div className="relative mt-5 space-y-2.5">
          <div aria-hidden="true" className="absolute top-5 bottom-5 left-[17px] w-px bg-gradient-to-b from-cyan-400 via-violet-400 to-mint-400 opacity-40" />
          {agents.map((agent, index) => (
            <div className="relative flex items-center gap-3 rounded-xl border border-line bg-surface p-3.5 transition hover:bg-raised" key={agent.name}>
              <span className={`relative z-10 size-2.5 rounded-full ${agent.color} shadow-[0_0_10px_currentColor]`} />
              <div className="min-w-0 flex-1">
                <p className="text-sm font-semibold text-copy">{agent.name}</p>
                <p className="text-xs text-subtle">{agent.role}</p>
              </div>
              <span className="font-mono text-[10px] text-subtle">0{index + 1}</span>
            </div>
          ))}
        </div>

        <div className="mt-5 grid grid-cols-3 gap-2">
          {[
            ['Input', 'CSV'],
            ['Modes', 'Guided / Auto'],
            ['Output', 'Explainable'],
          ].map(([label, value]) => (
            <div className="rounded-xl border border-line bg-surface p-3" key={label}>
              <p className="text-[10px] text-subtle uppercase">{label}</p>
              <p className="mt-1 truncate text-xs font-semibold text-muted">{value}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default function DashboardPage() {
  return (
    <>
      <section className="grid items-center gap-12 lg:grid-cols-[1.02fr_0.98fr] lg:gap-16">
        <div>
          <div className="inline-flex items-center gap-2 rounded-full border border-mint-400/20 bg-mint-400/[0.07] px-3 py-1.5 text-xs font-semibold text-mint-400">
            <span className="size-1.5 rounded-full bg-mint-400 shadow-[0_0_9px_#45e6c1]" />
            Agentic AutoML · Guided or fully automatic
          </div>
          <h1 className="text-gradient mt-7 max-w-3xl text-5xl leading-[0.98] font-bold tracking-[-0.055em] sm:text-6xl xl:text-7xl">
            Your data.<br />One intelligent flight plan.
          </h1>
          <p className="mt-7 max-w-xl text-lg leading-8 text-muted">
            Choose hands-on guidance or let DataPilot run end to end. Specialized AI agents profile, prepare, train, compare, and explain with every step kept visible.
          </p>
          <div className="mt-9 flex flex-col gap-3 sm:flex-row">
            <Link className="inline-flex items-center justify-center gap-3 rounded-xl bg-mint-400 px-5 py-3.5 text-sm font-bold text-night-950 shadow-[0_12px_35px_rgb(69_230_193/18%)] transition hover:-translate-y-0.5 hover:bg-[#6aefd0]" to="/upload">
              Launch an analysis <ArrowIcon />
            </Link>
            <Link className="inline-flex items-center justify-center rounded-xl border border-line bg-surface px-5 py-3.5 text-sm font-semibold text-copy transition hover:bg-raised" to="/runs/demo-run/progress">
              Explore the workflow
            </Link>
          </div>
          <div className="mt-10 flex flex-wrap gap-x-7 gap-y-3 text-xs font-medium text-subtle">
            {['Guided + Auto modes', 'Explainable results', 'Reusable pipelines'].map((item) => (
              <span className="flex items-center gap-2" key={item}>
                <svg aria-hidden="true" className="size-4 text-mint-400" fill="none" viewBox="0 0 20 20"><path d="m5 10 3 3 7-7" stroke="currentColor" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.8" /></svg>
                {item}
              </span>
            ))}
          </div>
        </div>
        <WorkflowPreview />
      </section>

      <section className="mt-20 border-y border-line py-8">
        <div className="grid gap-8 sm:grid-cols-3">
          {[
            ['01', 'Bring your data', 'Start with a familiar CSV dataset.'],
            ['02', 'Guide the agents', 'Confirm targets and follow each decision.'],
            ['03', 'Trust the outcome', 'Compare, explain, report, and predict.'],
          ].map(([number, title, copy]) => (
            <article className="flex gap-4" key={number}>
              <span className="font-mono text-xs font-bold text-electric-400">{number}</span>
              <div>
                <h2 className="text-base font-bold text-copy">{title}</h2>
                <p className="mt-1 text-sm leading-6 text-subtle">{copy}</p>
              </div>
            </article>
          ))}
        </div>
      </section>
    </>
  )
}
