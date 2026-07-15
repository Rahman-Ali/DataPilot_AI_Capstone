# DataPilot AI

DataPilot AI is an agent-driven AutoML platform that turns tabular datasets into transparent, reproducible machine-learning workflows. It coordinates specialized agents to inspect data, prepare features, compare models, explain results, generate reports, and serve predictions from a selected model.

The platform is designed around a simple principle: automation should accelerate decisions without hiding how those decisions were made. Users can choose between a guided workflow with confirmation points and a fully automatic workflow that runs end to end.

## Execution modes

| Mode | Behavior | Best suited for |
| --- | --- | --- |
| Guided | Pauses at important decisions so the user can confirm the target, problem type, columns, and workflow choices | Learning, review, experimentation, and higher-control analysis |
| Auto | Allows PilotFlow and the specialist agents to complete the workflow from dataset analysis through model results without manual confirmation | Fast baselines, repeatable analysis, and users who prefer full automation |

Both modes use the same transparent agent activity, stored run state, model comparison, explanations, reports, and prediction workflow. The selected mode changes the level of user involvement, not the visibility of the result.

## Core workflow

1. Upload a tabular CSV dataset.
2. Review its structure, quality, columns, and candidate target.
3. Select Guided or Auto execution mode.
4. Confirm key decisions in Guided mode, or allow Auto mode to proceed end to end.
5. Follow the agent workflow and its activity in real time.
6. Compare trained models and select the strongest result.
7. Review explanations, limitations, metrics, and generated artifacts.
8. Download a report or submit input to the saved prediction model.

## Agent architecture

| Agent | Responsibility |
| --- | --- |
| PilotFlow | Orchestrates the workflow and coordinates agent execution |
| DataLens | Profiles the dataset and summarizes data quality |
| CleanCraft | Builds a reusable preprocessing pipeline |
| ModelForge | Trains candidate models, compares metrics, and selects the best model |
| InsightBoard | Produces explanations, report content, and artifact metadata |

## Technology

### Frontend

- React and Vite
- React Router
- Tailwind CSS
- Responsive light and dark themes

### Backend and machine learning

- Django and Django REST Framework
- SQLite for application persistence
- LangGraph for workflow orchestration
- Pandas, NumPy, and Scikit-learn
- Joblib for pipeline and model persistence

Optional language-model providers can be integrated behind a provider interface with a deterministic fallback. Docker support will provide a reproducible local environment.

## Repository structure

```text
DataPilot_AI_Capstone/
|-- frontend/              # React application and frontend documentation
|-- backend/               # Django APIs, workflow agents, and ML services
|-- docs/                  # API contracts and shared technical documentation
|-- .github/               # Pull-request templates and repository configuration
|-- CONTRIBUTING.md        # Collaboration and review workflow
`-- README.md              # Platform overview
```

## Project status

| Area | Status |
| --- | --- |
| Repository governance and collaboration workflow | Complete |
| Frontend application foundation | Implemented and under review |
| Backend application foundation | Planned |
| Frontend/backend integration | Pending backend APIs |
| Agent execution and machine-learning pipeline | Planned |

The frontend currently provides the application shell, responsive navigation, persistent themes, safe error handling, and directly navigable screens for dataset upload, run progress, results, reports, and prediction. Progress values and agent activity are UI demonstration data until the backend status APIs are connected.

## Run the frontend

Requirements: a current Node.js and npm installation.

```powershell
cd frontend
npm install
npm run dev
```

Vite will print the local development address after startup.

### Frontend validation

```powershell
cd frontend
npm run lint
npm run build
```

Frontend-specific architecture, routes, and commands are documented in [`frontend/README.md`](frontend/README.md).

## Collaboration workflow

- `main` contains stable release and demonstration milestones.
- `dev` is the shared integration branch.
- Work is completed on focused `feature/...` or `chore/...` branches created from the latest `dev`.
- Pull requests from feature branches target `dev` and require review.
- `dev` reaches `main` only through a reviewed release pull request.
- Direct pushes and force-pushes to `main` and `dev` are not permitted.

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for branch naming, commit conventions, validation expectations, reviews, and conflict handling.

## Ownership

| Member | Primary area |
| --- | --- |
| Rahman Ali | Frontend architecture, application experience, visualizations, downloads, and prediction interface |
| Akbar Hussain | Backend APIs, persistence, agent orchestration, ML pipeline, artifacts, prediction service, and containerization |
| Shared | API contracts, integration, testing, documentation, reviews, and releases |

## Security and generated data

Never commit credentials, API keys, real environment files, uploaded datasets, local databases, generated models, reports, or runtime artifacts. Commit only source code, reviewed configuration, and safe templates such as `.env.example`.

The repository ignore rules protect common Node, Python, environment, database, upload, model, report, cache, IDE, and operating-system files.
