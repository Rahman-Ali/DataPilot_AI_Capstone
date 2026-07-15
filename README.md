# DataPilot AI

DataPilot AI is a three-week SharkStack capstone project for building a transparent, agent-driven AutoML workflow for tabular CSV datasets.

The MVP will guide a user through CSV upload, data analysis, preprocessing, model training and comparison, explainability, reporting, downloadable artifacts, and prediction with a saved model. The product prioritizes a stable and understandable end-to-end workflow over advanced MLOps features.

## Team

| Member | Primary responsibility |
| --- | --- |
| Rahman Ali | Frontend/UI lead: React, routes, workflow screens, charts, downloads, prediction form, and demo polish |
| Akbar Hussain | Backend/ML lead: Django APIs, persistence, LangGraph agents, ML pipeline, artifacts, prediction API, and Docker |
| Both | Integration, pull-request reviews, testing, explainability, mentor demos, documentation, and final rehearsal |

## Planned technology

- Frontend: React, Vite, Tailwind CSS, React Router, and a single charting library
- Backend: Django, Django REST Framework, and SQLite for the MVP
- Workflow: LangGraph
- Machine learning: Pandas, NumPy, Scikit-learn, and Joblib
- Optional explanation providers: Groq, Gemini, or OpenAI behind a rule-based fallback
- Delivery: Docker support and documented local setup

## Git workflow

- `main` is the stable mentor/demo branch.
- `dev` is the active integration branch.
- Each daily task uses a separate `feature/...` or `chore/...` branch created from the latest `dev`.
- Feature and chore pull requests target `dev` and require review by the other member.
- `dev` reaches `main` only through a mentor-approved release pull request.
- Direct pushes and force-pushes to `main` and `dev` are not allowed.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the complete collaboration process.

## Planned repository structure

```text
DataPilot_AI_Capstone/
|-- frontend/              # Rahman-owned React application
|-- backend/               # Akbar-owned Django, agent, and ML application
|-- docs/                  # Shared contracts, review notes, and demo material
|-- .github/               # Pull-request and repository collaboration templates
|-- CONTRIBUTING.md
`-- README.md
```

## Current status

Repository governance bootstrap. Application implementation has not started.

Setup and run commands will be added only after the Day 1 frontend and backend foundations have been implemented and verified.

## Security

Never commit API keys, credentials, real environment files, uploaded datasets, local databases, generated models, or reports. Commit only reviewed source code and safe examples such as `.env.example`.
