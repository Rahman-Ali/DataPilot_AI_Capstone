import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router'
import PageIntro from '../../components/ui/PageIntro.jsx'
import { api } from '../../lib/api.js'

const palette = ['#45e6c1', '#7c8cff', '#fbbf24', '#fb7185', '#38bdf8']

function ModelChart({ rows }) {
  const scores = rows.map((row) => Number(row.selection_score ?? row.score ?? 0))
  const low = Math.min(0, ...scores); const high = Math.max(...scores, 0.0001); const span = high - low || 1
  return <div className="mt-6 space-y-5">{rows.map((row, index) => <div key={row.model}><div className="mb-2 flex justify-between gap-4 text-sm"><span className="font-semibold text-copy">{row.model}</span><span className="font-mono text-muted">{scores[index].toFixed(5)}</span></div><div className="h-5 overflow-hidden rounded-full bg-raised"><div className="h-full rounded-full" style={{ background: palette[index], width: `${Math.max(2, (scores[index] - low) / span * 100)}%` }} /></div><p className="mt-1 text-[11px] text-subtle">Cross-validation {Number(row.cv_score).toFixed(5)} · tuned parameters {JSON.stringify(row.best_params)}</p></div>)}</div>
}

function QualityChart({ quality }) {
  return <div className="mt-6 grid gap-4 sm:grid-cols-3">{Object.entries(quality).map(([label, value], index) => <article className="rounded-2xl border border-line bg-raised p-5" key={label}><div className="flex items-end justify-between"><span className="text-sm font-semibold capitalize text-muted">{label}</span><strong className="text-2xl">{value}%</strong></div><div className="mt-4 h-3 rounded-full bg-canvas"><div className="h-full rounded-full" style={{ background: palette[index], width: `${value}%` }} /></div></article>)}</div>
}

function CorrelationMatrix({ matrix }) {
  if (!matrix.columns.length) return <p className="mt-5 text-muted">No numeric features are available for correlation.</p>
  const color = (value) => value >= 0 ? `rgba(69,230,193,${0.12 + Math.abs(value) * 0.78})` : `rgba(251,113,133,${0.12 + Math.abs(value) * 0.78})`
  return <div className="mt-6 overflow-auto"><div className="grid min-w-max gap-1" style={{ gridTemplateColumns: `9rem repeat(${matrix.columns.length}, 4.5rem)` }}><span />{matrix.columns.map((column) => <span className="truncate p-2 text-center text-[10px] text-muted" key={`head-${column}`} title={column}>{column}</span>)}{matrix.values.flatMap((row, rowIndex) => [<span className="truncate p-3 text-xs font-semibold text-muted" key={`row-${matrix.columns[rowIndex]}`}>{matrix.columns[rowIndex]}</span>, ...row.map((value, columnIndex) => <span className="grid aspect-square place-items-center rounded-lg text-xs font-bold text-night-950" key={`${rowIndex}-${columnIndex}`} style={{ background: color(value) }} title={`${matrix.columns[rowIndex]} × ${matrix.columns[columnIndex]} = ${value}`}>{value.toFixed(2)}</span>)])}</div><div className="mt-5 flex gap-5 text-xs text-muted"><span><i className="mr-2 inline-block size-3 rounded bg-rose-400" />negative</span><span><i className="mr-2 inline-block size-3 rounded bg-mint-400" />positive</span></div></div>
}

export default function RunVisualizationsPage() {
  const { runId } = useParams(); const [data, setData] = useState(null); const [error, setError] = useState('')
  useEffect(() => { api.results(runId).then(setData).catch((reason) => setError(reason.message)) }, [runId])
  return <><PageIntro description="Charts computed from DataLens profiling and ModelForge evaluation." eyebrow="Analysis graphics" status={data ? 'Live run data' : 'Loading'} title="Compare quality, relationships, and models." />{error && <p className="mt-8 text-red-300">{error}</p>}{data && <div className="mt-10 grid gap-6"><section className="rounded-3xl border border-line bg-surface p-6 sm:p-8"><h2 className="text-xl font-bold">Data quality</h2><p className="mt-2 text-sm text-muted">Completeness, duplicate-row uniqueness, and finite-value validity.</p><QualityChart quality={data.dataset.data_quality} /></section><section className="rounded-3xl border border-line bg-surface p-6 sm:p-8"><h2 className="text-xl font-bold">Model comparison</h2><p className="mt-2 text-sm text-muted">Held-out weighted F1 for classification or R² for regression.</p><ModelChart rows={data.leaderboard} /></section><section className="rounded-3xl border border-line bg-surface p-6 sm:p-8"><h2 className="text-xl font-bold">Correlation matrix</h2><p className="mt-2 text-sm text-muted">Pearson correlation for up to 20 numeric features. Green is positive; red is negative.</p><CorrelationMatrix matrix={data.dataset.correlation_matrix} /></section><Link className="w-fit rounded-xl bg-mint-400 px-5 py-3 font-bold text-night-950" to={`/runs/${runId}/results`}>Back to results</Link></div>}</>
}
