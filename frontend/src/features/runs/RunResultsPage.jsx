import { useEffect, useState } from 'react'
import { Link, Navigate, useParams } from 'react-router'
import PageIntro from '../../components/ui/PageIntro.jsx'
import { api } from '../../lib/api.js'

const formatMetric = (value) => typeof value === 'number' ? value.toFixed(5) : '—'

function EvaluationTable({ data }) {
  const classification = data.dataset.problem_type === 'classification'
  const columns = classification
    ? [['Train accuracy', 'train_accuracy'], ['Test accuracy', 'test_accuracy'], ['Train error', 'train_error_rate'], ['Test error', 'test_error_rate'], ['Test F1', 'test_f1_weighted']]
    : [['Train R²', 'train_r2'], ['Test R²', 'test_r2'], ['Train MAE', 'train_mae'], ['Test MAE', 'test_mae'], ['Train RMSE', 'train_rmse'], ['Test RMSE', 'test_rmse']]
  return <section className="overflow-auto rounded-3xl border border-line bg-surface p-6">
    <h2 className="text-xl font-bold">Training vs testing performance</h2>
    <p className="mt-2 text-sm text-muted">Testing metrics come from unseen held-out data. A large positive generalization gap can indicate overfitting.</p>
    <table className="mt-5 w-full min-w-[760px] text-left text-sm"><thead><tr><th className="border-b border-line p-3 text-electric-400">Model</th>{columns.map(([label]) => <th className="border-b border-line p-3 text-electric-400" key={label}>{label}</th>)}<th className="border-b border-line p-3 text-electric-400">Gap</th><th className="border-b border-line p-3 text-electric-400">Assessment</th></tr></thead>
      <tbody>{data.leaderboard.map((row) => <tr key={row.model}><td className="border-b border-line p-3 font-semibold text-copy">{row.model}</td>{columns.map(([, key]) => <td className="border-b border-line p-3 font-mono text-muted" key={key}>{formatMetric(row[key])}</td>)}<td className="border-b border-line p-3 font-mono text-muted">{formatMetric(row.generalization_gap)}</td><td className={`border-b border-line p-3 font-semibold ${row.overfitting_warning ? 'text-amber-300' : 'text-mint-400'}`}>{row.overfitting_warning ? 'Possible overfitting' : 'No large gap'}</td></tr>)}</tbody>
    </table>
  </section>
}

export default function RunResultsPage() {
  const { runId } = useParams()
  const [data, setData] = useState(null)
  const [error, setError] = useState('')
  useEffect(() => {
    if (runId !== 'demo-run') api.results(runId).then(setData).catch((reason) => setError(reason.message))
  }, [runId])
  const maxImportance = Math.max(...(data?.feature_contributions?.map((item) => item.importance) || [1]), 0.000001)

  if (runId === 'demo-run') return <Navigate replace to="/upload" />

  return (
    <>
      <PageIntro description={data?.summary || `Loading analysis ${runId}…`} eyebrow="Model results" status={data ? 'Analysis complete' : 'Loading'} title="The strongest model, with evidence." />
      {error && <div className="mt-8 rounded-xl border border-red-400/30 bg-red-400/10 p-4">
        <p className="text-red-300">{error}</p>
        <p className="mt-2 text-sm text-muted">Results exist after a dataset has completed the agent workflow.</p>
        <Link className="mt-4 inline-block rounded-lg bg-mint-400 px-4 py-2 text-sm font-bold text-night-950" to="/upload">Start a real analysis</Link>
      </div>}
      {data && <div className="mt-10 grid gap-6">
        <section className="grid gap-4 sm:grid-cols-4">
          {[['Problem', data.dataset.problem_type], ['Best model', data.best_model], ['Rows', data.dataset.rows], ['XAI method', data.explanation_method]].map(([label, value]) => <article className="rounded-2xl border border-line bg-surface p-5" key={label}><p className="text-xs text-subtle uppercase">{label}</p><p className="mt-2 font-bold text-copy">{value}</p></article>)}
        </section>
        <section className="rounded-3xl border border-line bg-surface p-6">
          <h2 className="text-xl font-bold">PilotFlow routing decision</h2>
          <p className="mt-3 text-muted">{data.routing.needs_cleaning ? `CleanCraft was required for: ${data.routing.reasons.join(', ')}.` : 'Dataset was already complete, numeric, and duplicate-free, so PilotFlow routed it directly to ModelForge.'}</p>
        </section>
        <EvaluationTable data={data} />
        <section className="overflow-auto rounded-3xl border border-line bg-surface p-6">
          <h2 className="text-xl font-bold">ModelForge leaderboard</h2>
          <p className="mt-2 text-sm text-muted">Models are tuned with cross-validation and regularized complexity controls. The detailed table above separates training and held-out testing results.</p>
          <table className="mt-5 w-full min-w-[560px] text-left text-sm"><thead><tr>{Object.keys(data.leaderboard[0]).map((key) => <th className="border-b border-line p-3 text-electric-400 capitalize" key={key}>{key}</th>)}</tr></thead><tbody>{data.leaderboard.map((row, index) => <tr className={index === 0 ? 'bg-mint-400/[0.06]' : ''} key={row.model}>{Object.keys(data.leaderboard[0]).map((key) => <td className="border-b border-line p-3 text-muted" key={key}>{row[key] != null ? (typeof row[key] === 'object' ? JSON.stringify(row[key]) : row[key]) : '—'}</td>)}</tr>)}</tbody></table>
        </section>
        <section className="rounded-3xl border border-line bg-surface p-6">
          <h2 className="text-xl font-bold">InsightBoard feature contributions</h2>
          <p className="mt-2 text-sm text-muted">Higher values indicate greater influence on model performance, calculated with {data.explanation_method}.</p>
          <div className="mt-6 space-y-4">{data.feature_contributions.slice(0, 12).map((item) => <div key={item.feature}><div className="mb-1 flex justify-between gap-4 text-sm"><span className="truncate text-copy">{item.feature}</span><span className="font-mono text-muted">{item.importance}</span></div><div className="h-2 rounded-full bg-raised"><div className="h-full rounded-full bg-gradient-to-r from-electric-400 to-mint-400" style={{ width: `${Math.max(2, item.importance / maxImportance * 100)}%` }} /></div></div>)}</div>
        </section>
        <div className="flex flex-wrap gap-3"><Link className="rounded-xl bg-mint-400 px-5 py-3 font-bold text-night-950" to={`/runs/${runId}/visualizations`}>Open analysis graphics</Link><Link className="rounded-xl border border-line bg-surface px-5 py-3 font-semibold" to={`/runs/${runId}/report`}>Report & downloads</Link><Link className="rounded-xl border border-line bg-surface px-5 py-3 font-semibold" to={`/predict/${data.model_id}`}>Try prediction API</Link></div>
      </div>}
    </>
  )
}
