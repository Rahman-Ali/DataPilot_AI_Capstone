import PageIntro from '../../components/ui/PageIntro.jsx'
import PlaceholderPanel from '../../components/ui/PlaceholderPanel.jsx'

export default function UploadPage() {
  return (
    <>
      <PageIntro
        description="Bring in a tabular dataset, inspect its structure, and begin a guided machine-learning workflow with confidence."
        eyebrow="Dataset intake"
        status="Secure intake"
        title="Turn a CSV into a clear flight plan."
      />
      <PlaceholderPanel
        description="A transparent intake flow keeps you informed before any analysis begins."
        steps={[
          { title: 'Choose your data', description: 'Start with a clean CSV containing the features you want to explore.' },
          { title: 'Verify the structure', description: 'Confirm the file, columns, and target before processing.' },
          { title: 'Launch DataPilot', description: 'Hand the approved dataset to the coordinated agent workflow.' },
        ]}
        title="From file to analysis"
      />
    </>
  )
}
