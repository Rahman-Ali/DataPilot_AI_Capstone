# DataPilot AI backend

The Django REST backend stores uploaded datasets and run state in SQLite and
executes the complete agent workflow:

`DataLens → PilotFlow decision → optional CleanCraft → ModelForge → InsightBoard`

## Run locally

```powershell
cd backend
.\datapilot\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

In a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The frontend uses
`http://127.0.0.1:8000/api` by default. Override this with `VITE_API_URL`.

## Implemented API

- `GET /api/health/`
- `GET /api/dashboard/`
- `POST /api/datasets/upload/`
- `POST /api/runs/start/`
- `GET /api/runs/{id}/status/`
- `GET /api/runs/{id}/results/`
- `GET /api/runs/{id}/artifacts/`
- `GET /api/models/{id}/predict/` (input schema)
- `POST /api/models/{id}/predict/`

Run verification with:

```powershell
python manage.py test automl
```
