import { Link, useParams } from 'react-router'
import PageIntro from '../../components/ui/PageIntro.jsx'
import PlaceholderPanel from '../../components/ui/PlaceholderPanel.jsx'

export default function RunResultsPage() {
  const { runId } = useParams()

  return (
    <>
      <PageIntro
        description={`Analysis ${runId} brings model comparisons, quality signals, and dataset insights into one readable view.`}
        eyebrow="Model results"
        status="Decision workspace"
        title="The strongest model, with the context to trust it."
      />
      <PlaceholderPanel
        description="Move from model ranking to practical understanding without losing the reasoning behind the choice."
        steps={[
          { title: 'Leaderboard', description: 'Compare candidate models with consistent metrics.' },
          { title: 'Best model', description: 'Highlight the selected model and why it performed well.' },
          { title: 'Data insights', description: 'Surface distributions, missing values, and feature importance.' },
        ]}
        title="Your analysis, organized"
      />
      <div className="mt-6 flex flex-wrap gap-3">
        <Link className="rounded-xl bg-mint-400 px-5 py-3 font-bold text-night-950 transition hover:bg-[#6aefd0]" to={`/runs/${runId}/report`}>Open explainability report</Link>
        <Link className="rounded-xl border border-line bg-surface px-5 py-3 font-semibold text-copy transition hover:bg-raised" to="/predict/demo-model">Try a prediction</Link>
      </div>
    </>
  )
}
