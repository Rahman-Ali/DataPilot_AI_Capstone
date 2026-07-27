import { useEffect, useState } from 'react'
import { useParams } from 'react-router'
import PageIntro from '../../components/ui/PageIntro.jsx'
import { api } from '../../lib/api.js'

export default function PredictionPage() {
  const { modelId } = useParams()
  const [schema, setSchema] = useState(null)
  const [values, setValues] = useState({})
  const [prediction, setPrediction] = useState(null)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  useEffect(() => { api.modelSchema(modelId).then(setSchema).catch((reason) => setError(reason.message)) }, [modelId])
  async function submit(event) {
    event.preventDefault(); setBusy(true); setError(''); setPrediction(null)
    try { setPrediction(await api.predict(modelId, values)) } catch (reason) { setError(reason.message) } finally { setBusy(false) }
  }
  return (
    <>
      <PageIntro description={schema ? `${schema.name} predicts ${schema.target} using the saved preprocessing pipeline.` : `Loading model ${modelId}…`} eyebrow="Prediction API" status="Schema validated" title="Move from model to prediction." />
      <form className="panel-glow mt-10 rounded-3xl border border-line bg-surface p-6 sm:p-8" onSubmit={submit}>
        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">{schema?.features.map((feature) => <label className="text-sm font-semibold text-muted" key={feature.name}>{feature.name}<input className="mt-2 block w-full rounded-xl border border-line bg-raised px-4 py-3 text-copy" onChange={(event) => setValues((current) => ({ ...current, [feature.name]: event.target.value }))} required step="any" type={feature.type === 'number' ? 'number' : 'text'} /></label>)}</div>
        {error && <p className="mt-5 rounded-xl bg-red-400/10 p-4 text-red-300">{error}</p>}
        {prediction && <div className="mt-6 rounded-2xl border border-mint-400/30 bg-mint-400/10 p-5"><p className="text-xs font-bold text-mint-400 uppercase">Predicted {prediction.target}</p><p className="mt-2 text-3xl font-bold text-copy">{String(prediction.prediction)}</p></div>}
        <button className="mt-6 rounded-xl bg-mint-400 px-6 py-3 font-bold text-night-950 disabled:opacity-50" disabled={!schema || busy} type="submit">{busy ? 'Predicting…' : 'Get prediction'}</button>
      </form>
    </>
  )
}
