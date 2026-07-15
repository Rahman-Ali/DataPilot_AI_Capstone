import { useState } from 'react'
import PageIntro from '../../components/ui/PageIntro.jsx'
import PlaceholderPanel from '../../components/ui/PlaceholderPanel.jsx'

const modes = [
  {
    id: 'guided',
    label: 'Guided mode',
    description: 'Pause at important decisions to confirm the target, problem type, columns, and workflow choices.',
    accent: 'text-electric-400',
  },
  {
    id: 'auto',
    label: 'Auto mode',
    description: 'Let PilotFlow coordinate the complete workflow automatically from dataset analysis to results.',
    accent: 'text-mint-400',
  },
]

export default function UploadPage() {
  const [mode, setMode] = useState('guided')
  const isAuto = mode === 'auto'

  return (
    <>
      <PageIntro
        description="Bring in a tabular dataset, choose how involved you want to be, and begin a transparent machine-learning workflow."
        eyebrow="Dataset intake"
        status="Secure intake"
        title="Turn a CSV into a clear flight plan."
      />

      <section className="mt-10" aria-labelledby="mode-heading">
        <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-[11px] font-bold tracking-[0.18em] text-mint-400 uppercase">Execution preference</p>
            <h2 className="mt-2 text-xl font-bold text-copy" id="mode-heading">Choose your level of control</h2>
          </div>
          <p className="text-sm text-muted">You can review the selected mode before starting a run.</p>
        </div>

        <div className="mt-5 grid gap-4 sm:grid-cols-2" role="radiogroup" aria-label="Execution mode">
          {modes.map((option) => {
            const selected = mode === option.id

            return (
              <button
                aria-checked={selected}
                className={`group relative rounded-2xl border p-5 text-left transition sm:p-6 ${
                  selected
                    ? 'border-electric-400/45 bg-electric-400/[0.07] shadow-[0_18px_45px_rgb(86_103_220/10%)]'
                    : 'border-line bg-surface hover:bg-raised'
                }`}
                key={option.id}
                onClick={() => setMode(option.id)}
                role="radio"
                type="button"
              >
                <span className="flex items-center justify-between gap-4">
                  <span className={`text-base font-bold ${option.accent}`}>{option.label}</span>
                  <span className={`grid size-5 place-items-center rounded-full border ${selected ? 'border-electric-400' : 'border-subtle'}`}>
                    {selected && <span className="size-2.5 rounded-full bg-electric-400" />}
                  </span>
                </span>
                <span className="mt-3 block text-sm leading-6 text-muted">{option.description}</span>
              </button>
            )
          })}
        </div>
      </section>

      <PlaceholderPanel
        description={
          isAuto
            ? 'PilotFlow will coordinate the complete agent workflow automatically while keeping every action visible.'
            : 'DataPilot will pause at important decisions so you can review and confirm the workflow.'
        }
        steps={[
          { title: 'Choose your data', description: 'Start with a clean CSV containing the features you want to explore.' },
          {
            title: isAuto ? 'Analyze automatically' : 'Review key decisions',
            description: isAuto
              ? 'The agents will infer the workflow and proceed without confirmation pauses.'
              : 'Confirm the target, problem type, columns, and preparation choices.',
          },
          {
            title: 'Launch DataPilot',
            description: `${isAuto ? 'Auto' : 'Guided'} mode will be recorded with the run before agent execution begins.`,
          },
        ]}
        title={`${isAuto ? 'Automatic' : 'Guided'} path from file to analysis`}
      />
    </>
  )
}
