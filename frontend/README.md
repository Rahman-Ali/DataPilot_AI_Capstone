# DataPilot AI Frontend

The DataPilot AI frontend is a responsive React application for running guided or fully automatic workflows across dataset intake, agent execution, model comparison, explainability, reporting, and prediction.

This directory is an independently installable frontend workspace. Platform-wide architecture, ownership, and collaboration guidance remain in the [root README](../README.md).

## Technology

- React
- Vite
- React Router
- Tailwind CSS
- Oxlint

## Application structure

```text
src/
|-- app/                   # Route composition and application entry
|-- components/
|   |-- layout/            # Shared navigation and page layout
|   `-- ui/                # Reusable interface components
|-- features/
|   |-- dashboard/
|   |-- upload/
|   |-- runs/
|   |-- reports/
|   |-- predictions/
|   `-- not-found/
|-- index.css              # Tailwind import, design tokens, and theme variables
`-- main.jsx               # Browser router, theme initialization, and error boundary
```

## Routes

| Route | Purpose |
| --- | --- |
| `/` | DataPilot workspace overview |
| `/upload` | Dataset intake |
| `/runs/:runId/progress` | Agent progress and activity |
| `/runs/:runId/results` | Model comparison and dataset insights |
| `/runs/:runId/report` | Explainability and report artifacts |
| `/predict/:modelId` | Saved-model prediction workspace |
| `*` | Safe not-found experience |

## Execution modes

- **Guided mode** presents confirmation points for the target, problem type, columns, and workflow decisions.
- **Auto mode** runs the agent workflow end to end without requiring manual confirmation.

Both modes share the same routes and progress experience. Backend run data will determine whether confirmation controls are shown and when the workflow is allowed to continue.

## Local development

Requirements: a current Node.js and npm installation.

```powershell
npm install
npm run dev
```

Vite prints the local development URL after startup, normally `http://localhost:5173`.

## Validation

```powershell
npm run lint
npm run build
```

The production build is written to `dist/`, which is intentionally excluded from version control.

## Themes

The interface supports light and dark themes through shared CSS design tokens. The selected theme is stored in browser `localStorage` under `datapilot-theme`; the operating-system preference is used when no selection has been saved.

When adding a component, use the semantic theme utilities such as `bg-canvas`, `bg-surface`, `text-copy`, `text-muted`, and `border-line` so it remains readable in both themes.

## Backend integration boundary

The current progress percentage, agent states, timestamps, dataset summary, and activity messages are demonstration values. They are intentionally isolated in feature components so backend API responses can replace them without changing the route or layout architecture.

Frontend code must not contain API credentials, provider secrets, uploaded datasets, generated reports, model files, or backend persistence logic.
