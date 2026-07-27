import { useEffect, useState } from 'react'
import { Link, Navigate, useParams } from 'react-router'
import PageIntro from '../../components/ui/PageIntro.jsx'
import { api } from '../../lib/api.js'

const agents = ['PilotFlow', 'DataLens', 'CleanCraft', 'ModelForge', 'InsightBoard']

export default function RunProgressPage() {
  const { runId } = useParams()
  const [run, setRun] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    if (runId === 'demo-run') return undefined
    let timer
    const load = () => api.status(runId).then((data) => {
      setRun(data)
      if (!['completed', 'failed'].includes(data.status)) timer = setTimeout(load, 1200)
    }).catch((reason) => setError(reason.message))
    load()
    return () => clearTimeout(timer)
  }, [runId])

  if (runId === 'demo-run') return <Navigate replace to="/upload" />

  const completeAgents = new Set(run?.logs?.map((log) => log.agent) || [])
  return (
    <>
      <PageIntro description={`Run ${runId} exposes every agent decision made by the Django workflow.`} eyebrow="Run tracking" status={run?.status || 'Loading'} title="Every decision, visible." />
      <section className="panel-glow mt-10 rounded-3xl border border-line bg-surface p-6 sm:p-8">
        {error && <div className="rounded-xl border border-red-400/30 bg-red-400/10 p-4">
          <p className="text-red-300">{error}</p>
          <p className="mt-2 text-sm text-muted">Run pages work after Django creates a run from an uploaded dataset.</p>
          <Link className="mt-4 inline-block rounded-lg bg-mint-400 px-4 py-2 text-sm font-bold text-night-950" to="/upload">Start a real analysis</Link>
        </div>}
        <div className="flex items-end justify-between"><div><p className="text-sm text-muted">{run?.status === 'failed' ? 'Workflow stopped at' : 'Current agent'}</p><h2 className={`mt-1 text-2xl font-bold ${run?.status === 'failed' ? 'text-red-300' : ''}`}>{run?.current_agent || 'Connecting…'}</h2><p className="mt-1 text-xs text-subtle">{run?.status === 'failed' ? 'This run failed and is no longer processing.' : `Current agent ${run?.agent_progress || 0}% complete`}</p></div><p className={`font-mono text-4xl font-bold ${run?.status === 'failed' ? 'text-red-300' : ''}`}>{run?.progress || 0}%</p></div>
        {run?.target_selection_reason && <div className="mt-5 rounded-xl border border-electric-400/20 bg-electric-400/[0.06] p-4"><p className="text-xs font-bold text-electric-400 uppercase">{run.mode} target · {run.target_column}</p><p className="mt-1 text-sm text-muted">{run.target_selection_reason}</p><p className="mt-2 text-xs text-subtle">Algorithms: {run.selected_algorithms.join(', ')}</p></div>}
        <div className="mt-6 h-3 overflow-hidden rounded-full bg-raised"><div className="h-full bg-gradient-to-r from-electric-400 to-mint-400 transition-all" style={{ width: `${run?.progress || 0}%` }} /></div>
        <div className="mt-8 grid gap-3 sm:grid-cols-5">
          {agents.map((agent) => <div className={`rounded-xl border p-3 ${run?.current_agent === agent ? 'border-electric-400 bg-electric-400/10' : 'border-line bg-raised'}`} key={agent}><span className={`mr-2 inline-block size-2 rounded-full ${completeAgents.has(agent) ? 'bg-mint-400' : 'bg-subtle'}`} /> <span className="text-xs font-bold">{agent}</span></div>)}
        </div>
        <div className="mt-8 space-y-3">{run?.logs?.map((log, index) => <article className="rounded-xl border border-line bg-raised p-4" key={`${log.time}-${index}`}><p className="text-xs font-bold text-electric-400">{log.agent}</p><p className="mt-1 text-sm text-muted">{log.message}</p></article>)}</div>
        {run?.error && <div className="mt-5 rounded-xl border border-red-400/30 bg-red-400/10 p-4"><p className="font-bold text-red-300">Workflow failed</p><p className="mt-2 text-sm text-red-300">{run.error}</p><Link className="mt-4 inline-block rounded-lg bg-mint-400 px-4 py-2 text-sm font-bold text-night-950" to="/upload">Start a corrected run</Link></div>}
        {run?.status === 'completed' && <Link className="mt-7 inline-block rounded-xl bg-mint-400 px-6 py-3 font-bold text-night-950" to={`/runs/${runId}/results`}>View results</Link>}
      </section>
    </>
  )
}
