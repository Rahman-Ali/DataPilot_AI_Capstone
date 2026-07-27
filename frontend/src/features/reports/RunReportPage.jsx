import { useEffect, useState } from 'react'
import { useParams } from 'react-router'
import PageIntro from '../../components/ui/PageIntro.jsx'
import { api } from '../../lib/api.js'

export default function RunReportPage() {
  const { runId } = useParams()
  const [results, setResults] = useState(null)
  const [artifacts, setArtifacts] = useState([])
  const [error, setError] = useState('')
  useEffect(() => { Promise.all([api.results(runId), api.artifacts(runId)]).then(([result, files]) => { setResults(result); setArtifacts(files.artifacts) }).catch((reason) => setError(reason.message)) }, [runId])
  return (
    <>
      <PageIntro description="A stored, explainable record of the workflow, model selection, and generated files." eyebrow="InsightBoard report" status="Explainable by design" title="Understand what won and why." />
      {error && <p className="mt-8 text-red-300">{error}</p>}
      {results && <div className="mt-10 grid gap-6 lg:grid-cols-[1.3fr_.7fr]">
        <section className="rounded-3xl border border-line bg-surface p-6 sm:p-8"><h2 className="text-xl font-bold">Executive summary</h2><p className="mt-4 leading-7 text-muted">{results.summary}</p><h3 className="mt-7 font-bold">Data preparation</h3><p className="mt-2 text-sm leading-6 text-muted">{results.preprocessing.applied ? `CleanCraft processed ${results.preprocessing.numeric_columns.length} numeric and ${results.preprocessing.categorical_columns.length} categorical features, removed duplicates, imputed missing values, encoded categories, and standardized numeric data.` : 'PilotFlow found no missing, duplicate, or categorical feature issues. CleanCraft was safely bypassed.'}</p><h3 className="mt-7 font-bold">Interpretation</h3><p className="mt-2 text-sm leading-6 text-muted">The top contributing features were {results.feature_contributions.slice(0, 3).map((item) => item.feature).join(', ') || 'not distinguishable'}. Contribution describes model influence, not causation.</p></section>
        <aside className="rounded-3xl border border-line bg-surface p-6"><h2 className="text-xl font-bold">Downloads</h2><div className="mt-5 space-y-3">{artifacts.map((artifact) => <a className="block rounded-xl border border-line bg-raised p-4 transition hover:border-electric-400" href={artifact.url} key={artifact.id} rel="noreferrer" target="_blank"><span className="block font-bold text-copy">{artifact.name}</span><span className="mt-1 block text-xs text-muted">{artifact.kind.replaceAll('_', ' ')}</span></a>)}</div></aside>
      </div>}
    </>
  )
}
