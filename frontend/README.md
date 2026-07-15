# DataPilot AI Frontend

React and Vite interface for the DataPilot AI capstone. The Day 1 foundation provides reusable navigation, route placeholders, responsive styling, a not-found page, and a safe application error fallback.

## Local development

```powershell
npm install
npm run dev
```

Vite prints the local URL after startup. The usual address is `http://localhost:5173`.

## Validation

```powershell
npm run lint
npm run build
```

## Current routes

- `/`
- `/upload`
- `/runs/:runId/progress`
- `/runs/:runId/results`
- `/runs/:runId/report`
- `/predict/:modelId`

API calls, charts, machine-learning logic, and backend integration are intentionally outside the Day 1 frontend scope.
