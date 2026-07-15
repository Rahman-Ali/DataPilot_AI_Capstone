import { useParams } from 'react-router'
import PageIntro from '../../components/ui/PageIntro.jsx'
import PlaceholderPanel from '../../components/ui/PlaceholderPanel.jsx'

export default function RunReportPage() {
  const { runId } = useParams()

  return (
    <>
      <PageIntro
        description={`Analysis ${runId} translates technical results into a narrative your team can review and share.`}
        eyebrow="Explainability report"
        status="Explainable by design"
        title="Understand not only what won, but why."
      />
      <PlaceholderPanel
        description="Bring model reasoning, limitations, and useful outputs together in one accountable record."
        steps={[
          { title: 'Executive summary', description: 'Translate the run into concise, human-readable findings.' },
          { title: 'Explanations', description: 'Describe important features, limitations, and model behavior.' },
          { title: 'Downloads', description: 'Collect approved reports and model artifacts in one place.' },
        ]}
        title="A report built for real decisions"
      />
    </>
  )
}
