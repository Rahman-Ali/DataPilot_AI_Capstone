import { useState } from 'react'
import { useNavigate } from 'react-router'
import PageIntro from '../../components/ui/PageIntro.jsx'
import { api } from '../../lib/api.js'

export default function UploadPage() {
  const navigate = useNavigate()
  const [mode, setMode] = useState('auto')
  const [file, setFile] = useState(null)
  const [dataset, setDataset] = useState(null)
  const [target, setTarget] = useState('')
  const [algorithms, setAlgorithms] = useState([])
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  async function inspect(event) {
    const selected = event.target.files?.[0]
    if (!selected) return
    setFile(selected); setBusy(true); setError('')
    try {
      const uploaded = await api.upload(selected)
      const recommended = uploaded.target_recommendation.column
      setDataset(uploaded); setTarget(recommended)
      setAlgorithms(uploaded.algorithm_catalog[uploaded.target_options[recommended]])
    } catch (reason) { setDataset(null); setError(reason.message) } finally { setBusy(false) }
  }

  function chooseTarget(value) {
    setTarget(value)
    setAlgorithms(dataset.algorithm_catalog[dataset.target_options[value]])
  }

  function toggleAlgorithm(name) {
    setAlgorithms((current) => current.includes(name) ? current.filter((item) => item !== name) : [...current, name])
  }

  async function launch() {
    setBusy(true); setError('')
    try {
      const guided = mode === 'guided' ? { target_column: target, algorithms } : {}
      const run = await api.startRun({ dataset_id: dataset.id, mode, ...guided })
      navigate(`/runs/${run.run_id}/progress`)
    } catch (reason) { setError(reason.message); setBusy(false) }
  }

  return <>
    <PageIntro description="Auto mode chooses and explains the target. Guided mode gives you control over the target and algorithms." eyebrow="Dataset intake" status="Backend connected" title="Configure a real AutoML mission." />
    <section className="panel-glow mt-10 rounded-3xl border border-line bg-surface p-6 sm:p-8">
      <div className="grid gap-6 lg:grid-cols-2">
        <label className="grid min-h-48 cursor-pointer place-items-center rounded-2xl border border-dashed border-electric-400/40 bg-electric-400/[0.04] p-8 text-center">
          <span><span className="block text-lg font-bold text-copy">{file ? file.name : 'Choose a CSV dataset'}</span><span className="mt-2 block text-sm text-muted">Maximum 10 MB · at least 20 rows</span></span>
          <input accept=".csv,text/csv" className="sr-only" disabled={busy} onChange={inspect} type="file" />
        </label>
        <div><p className="text-xs font-bold tracking-widest text-mint-400 uppercase">Execution mode</p><div className="mt-4 grid gap-3">
          {[['auto', 'PilotFlow selects the target and records a transparent reason.'], ['guided', 'You choose the target and exactly which algorithms are trained.']].map(([item, copy]) => <button className={`rounded-xl border p-4 text-left ${mode === item ? 'border-electric-400 bg-electric-400/10' : 'border-line bg-raised'}`} key={item} onClick={() => setMode(item)} type="button"><span className="font-bold capitalize text-copy">{item} mode</span><span className="mt-1 block text-xs text-muted">{copy}</span></button>)}
        </div></div>
      </div>
      {dataset && <div className="mt-7 rounded-2xl border border-line bg-raised p-5">
        <div className="flex flex-wrap items-end justify-between gap-4"><div><p className="font-bold text-copy">{dataset.rows.toLocaleString()} rows · {dataset.columns} columns</p><p className="mt-1 text-xs text-muted">Problem type is inferred from the selected target.</p></div>
          {mode === 'guided' ? <label className="text-sm font-semibold text-muted">Target column<select className="ml-3 rounded-lg border border-line bg-canvas px-3 py-2 text-copy" onChange={(event) => chooseTarget(event.target.value)} value={target}>{dataset.column_names.map((column) => <option key={column}>{column}</option>)}</select></label> : <div className="max-w-xl rounded-xl border border-mint-400/25 bg-mint-400/[0.06] p-4 text-sm"><span className="font-bold text-mint-400">Auto target: {dataset.target_recommendation.column}</span><p className="mt-1 text-xs leading-5 text-muted">{dataset.target_recommendation.reason}</p></div>}
        </div>
        {mode === 'guided' && <div className="mt-5"><p className="text-xs font-bold tracking-widest text-electric-400 uppercase">Algorithms to train · {dataset.target_options[target]}</p><div className="mt-3 flex flex-wrap gap-3">{dataset.algorithm_catalog[dataset.target_options[target]].map((name) => <label className={`cursor-pointer rounded-xl border px-4 py-3 text-sm font-semibold ${algorithms.includes(name) ? 'border-mint-400 bg-mint-400/10 text-copy' : 'border-line text-muted'}`} key={name}><input checked={algorithms.includes(name)} className="mr-2 accent-[#45e6c1]" onChange={() => toggleAlgorithm(name)} type="checkbox" />{name}</label>)}</div></div>}
        <div className="mt-5 overflow-auto"><table className="w-full min-w-max text-left text-xs"><thead><tr>{dataset.column_names.map((column) => <th className="border-b border-line p-2 text-electric-400" key={column}>{column}</th>)}</tr></thead><tbody>{dataset.preview.slice(0, 5).map((row, index) => <tr key={index}>{dataset.column_names.map((column) => <td className="border-b border-line p-2 text-muted" key={column}>{String(row[column] ?? '—')}</td>)}</tr>)}</tbody></table></div>
      </div>}
      {error && <p className="mt-5 rounded-xl border border-red-400/30 bg-red-400/10 p-4 text-sm text-red-300">{error}</p>}
      <button className="mt-6 rounded-xl bg-mint-400 px-6 py-3 font-bold text-night-950 disabled:cursor-not-allowed disabled:opacity-50" disabled={!dataset || busy || (mode === 'guided' && algorithms.length === 0)} onClick={launch} type="button">{busy ? 'Starting workflow…' : 'Launch agent workflow'}</button>
    </section>
  </>
}
