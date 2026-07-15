import { useParams } from 'react-router'
import PageIntro from '../../components/ui/PageIntro.jsx'
import PlaceholderPanel from '../../components/ui/PlaceholderPanel.jsx'

export default function PredictionPage() {
  const { modelId } = useParams()

  return (
    <>
      <PageIntro
        description={`Use saved model ${modelId} with the exact feature structure learned during training.`}
        eyebrow="Prediction workspace"
        status="Schema guided"
        title="Move from trained model to useful prediction."
      />
      <PlaceholderPanel
        description="A guided flow will validate every value before asking the selected model for an outcome."
        steps={[
          { title: 'Load schema', description: 'Build inputs from the selected model’s saved feature schema.' },
          { title: 'Validate values', description: 'Guide users toward complete and correctly typed input.' },
          { title: 'Show prediction', description: 'Return the outcome with clear status and context.' },
        ]}
        title="A predictable path to prediction"
      />
    </>
  )
}
