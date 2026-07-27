# DataPilot AI — Complete Project Working Guide

## 1. Project purpose

DataPilot AI is a web-based AutoML application for CSV/tabular data. A user uploads a dataset, chooses the column to predict, and starts a workflow that:

1. studies the dataset,
2. decides whether corrective cleaning is necessary,
3. builds a safe preprocessing pipeline,
4. trains and tunes several machine-learning models,
5. selects the strongest model,
6. explains the result,
7. saves downloadable files and a reusable prediction model.

The main goal is to make a machine-learning workflow usable from a browser while keeping the important decisions visible.

> **Important implementation fact:** the named “agents” are currently deterministic Python methods in `backend/automl/pipeline.py`. They are not separate servers, background workers, or LLM agents. `AgentWorkflow` calls them in sequence and stores their activity as logs. The repository README mentions LangGraph and optional LLM integration as architectural direction, but the active code does not currently use them.

## 2. Technology and major folders

| Area | Technology | Purpose |
| --- | --- | --- |
| `frontend/` | React, Vite, React Router, Tailwind CSS | Browser UI, navigation, forms, result display, and API calls |
| `backend/` | Django, Django REST Framework | HTTP API, validation, database access, workflow execution, and file serving |
| `backend/automl/pipeline.py` | Pandas, NumPy, scikit-learn, Joblib | Dataset analysis, preprocessing, training, evaluation, explainability, and model saving |
| `backend/db.sqlite3` | SQLite | Stores structured application records and relationships |
| `backend/runtime/` | Filesystem storage | Stores uploaded CSVs, trained `.joblib` models, cleaned datasets, and JSON reports |
| `docs/` | Markdown | Shared API-contract documentation |

Important source files:

| File | Responsibility |
| --- | --- |
| `frontend/src/app/App.jsx` | Declares frontend routes/pages |
| `frontend/src/lib/api.js` | Central wrapper around browser `fetch` calls |
| `frontend/src/features/upload/UploadPage.jsx` | Dataset upload, preview, mode, target selection, and run launch |
| `frontend/src/features/runs/RunProgressPage.jsx` | Run status, progress, agent logs, and failure display |
| `frontend/src/features/runs/RunResultsPage.jsx` | Dataset summary, routing, leaderboard, and feature importance |
| `frontend/src/features/reports/RunReportPage.jsx` | Human-readable report and artifact download links |
| `frontend/src/features/predictions/PredictionPage.jsx` | Dynamic prediction form and prediction result |
| `backend/config/settings.py` | Django, SQLite, CORS, upload limit, and media configuration |
| `backend/config/urls.py` | Root, admin, API, and development media routes |
| `backend/automl/urls.py` | All application API URL patterns |
| `backend/automl/views.py` | Request validation and endpoint responses |
| `backend/automl/models.py` | SQLite data model |
| `backend/automl/pipeline.py` | Complete five-stage agent workflow |

## 3. High-level request flow

```text
Browser page
   │
   │ calls api.* from frontend/src/lib/api.js
   ▼
fetch(http://127.0.0.1:8000/api/...)
   │
   ▼
Django config/urls.py
   │ includes /api/
   ▼
automl/urls.py
   │ selects a view
   ▼
automl/views.py
   ├── validates request/file/JSON
   ├── reads or writes Django models → db.sqlite3
   ├── starts AgentWorkflow when requested
   └── returns a JSON Response
   │
   ▼
frontend state is updated and React renders the result
```

The frontend API base is `VITE_API_URL` when that environment variable exists; otherwise it is `http://127.0.0.1:8000/api`. Django allows the Vite development origins `http://localhost:5173` and `http://127.0.0.1:5173` through CORS.

## 4. Complete user journey

### Step 1 — Open the application

The React route `/` displays the marketing/dashboard landing page. It describes the five agents and links to `/upload`. This page currently uses static presentation data; it does **not** call the backend `/api/dashboard/` endpoint.

### Step 2 — Upload and inspect a CSV

On `/upload`, selecting a file calls:

```http
POST /api/datasets/upload/
Content-Type: multipart/form-data
file=<CSV file>
```

The backend checks that a file exists, its extension is `.csv`, it is no larger than 10 MB, Pandas can read it, it has rows, and it has at least two columns. It then saves:

- file metadata and a ten-row JSON-safe preview in SQLite;
- the actual uploaded CSV under `backend/runtime/datasets/`.

The response supplies the dataset UUID, dimensions, column names, and preview. React displays the first five preview rows and initially selects the last column as the target.

### Step 3 — Choose mode and target

The user selects `auto` or `guided` and chooses the target column.

Current behavior of the modes:

- `auto`: scores every column using transparent name, position, cardinality, identifier, and completeness rules; it selects the target, displays/stores its reason, and trains all compatible algorithms.
- `guided`: requires the user to choose a target and one or more compatible algorithms; the backend validates and trains only that selection.

Guided mode provides configuration control before execution; it does not pause between agents after launch.

### Step 4 — Start the workflow

The frontend sends:

```json
POST /api/runs/start/
{
  "dataset_id": "<dataset UUID>",
  "target_column": "<selected column>",
  "mode": "auto"
}
```

Django validates the dataset, target, and mode, creates a `Run` row, then calls `AgentWorkflow(run).execute()`.

> **Live execution behavior:** the endpoint returns HTTP 202 immediately and starts `AgentWorkflow` in a background Django thread after the database transaction commits. The progress page polls every 1.2 seconds and displays current agent, agent progress, overall progress, and logs. A production deployment should replace the in-process thread with a durable Celery/Redis worker.

### Step 5 — Agent workflow

The active sequence is:

```text
DataLens
   ↓
PilotFlow
   ├── blocking problem → fail run
   ├── corrective issues → CleanCraft
   └── no corrective issues → bypass CleanCraft
                              ↓
                         ModelForge
                              ↓
                        InsightBoard
                              ↓
              persist results, model, and artifacts
```

Each `log()` call updates `Run.current_agent`, `Run.progress`, and the JSON `Run.logs` list in SQLite.

### Step 6 — Results and report

After navigation to `/runs/{runId}/progress`, the frontend reads status and displays the stored agent logs. A completed run links to `/runs/{runId}/results`, which requests the full results JSON and displays:

- inferred classification/regression type,
- chosen model,
- row count,
- routing decision,
- model leaderboard and metrics,
- feature contributions.

The report page requests results and artifacts together. It explains preprocessing and provides links to files served from `/media/` during Django development.

### Step 7 — Prediction

The results contain a trained-model UUID. `/predict/{modelId}` first requests the saved feature schema and builds the correct number/text input fields. On submission, Django validates all required features, loads the saved Joblib object, runs its preprocessing-and-model pipeline, decodes a text classification target if needed, and returns the prediction.

## 5. Detailed responsibilities of every agent

### DataLens — dataset profiler

DataLens is the first analytical stage. It:

- verifies that the target exists;
- requires at least 20 rows and at least one feature plus one target;
- rejects a completely empty target;
- infers classification or regression and records confidence/reasons;
- detects numeric and categorical columns;
- reports missing, infinite, duplicate, constant, possible identifier, and high-cardinality columns;
- diagnoses different numeric scales and possible IQR outliers;
- calculates numeric statistics;
- calculates classification distribution and imbalance ratio.

Problem-type inference is rule-based. Non-numeric, Boolean, binary, and low-cardinality numeric targets are classification; higher-cardinality numeric targets are regression.

### PilotFlow — orchestrator and router

PilotFlow examines the DataLens profile and makes the route decision.

Corrective-cleaning reasons include missing target/features, duplicate rows, infinite numeric values, and constant features. Warnings include categorical encoding, different scales, high cardinality, identifiers, outliers, and severe class imbalance.

It also blocks impossible cases, such as no features, fewer than two classification classes, or a class with fewer than two samples. If correction is needed it routes to CleanCraft; otherwise it bypasses corrective cleaning and proceeds toward ModelForge. Preprocessing inside the model pipeline still occurs even when CleanCraft is bypassed.

### CleanCraft — corrective data cleaner

CleanCraft only runs when PilotFlow finds corrective issues. It:

- converts positive/negative infinity to missing values;
- removes duplicate rows;
- removes rows with missing targets;
- removes constant feature columns;
- validates that usable rows/features remain;
- saves `cleaned_dataset.csv` as a downloadable artifact.

It deliberately does not globally fit statistical transformations before the train/test split. Median imputation and scaling for numbers, and most-frequent imputation plus one-hot encoding for categories, remain inside the scikit-learn pipeline. This reduces data leakage.

When CleanCraft is bypassed, PilotFlow still builds the same model transformation pipeline. “Bypassed” means no corrective dataset rewrite, not no preprocessing.

### ModelForge — trainer and model selector

ModelForge:

- creates an 80/20 train/test split with random seed 42;
- uses stratification for classification where safely possible;
- creates up to five-fold `StratifiedKFold` or `KFold` validation;
- combines preprocessing and estimator in one scikit-learn `Pipeline`;
- performs `RandomizedSearchCV` with up to 12 parameter combinations per algorithm;
- evaluates three candidates;
- chooses the best by weighted F1 for classification or R² for regression;
- stores metrics, cross-validation score, and best hyperparameters;
- saves the selected pipeline as a Joblib file;
- creates a `TrainedModel` SQLite record with the prediction input schema.

Classification candidates are Logistic Regression, Random Forest Classifier, and Gradient Boosting Classifier. Regression candidates are Ridge Regression, Random Forest Regressor, and Gradient Boosting Regressor.

Classification metrics include accuracy, balanced accuracy, weighted precision/recall/F1, and macro F1. Regression metrics include R², MAE, and RMSE.

### InsightBoard — explanations and reporting

InsightBoard:

- calculates global permutation feature importance on the held-out test set;
- attempts a local linear-surrogate explanation inspired by LIME;
- safely falls back to permutation importance if the local explanation fails;
- builds the final nested report plus backward-compatible fields used by the UI;
- saves `report.json` as an artifact;
- marks the final progress at 100%.

Feature contribution indicates predictive influence, not causation.

## 6. Every backend endpoint

### Non-API/service endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/` | Returns small JSON showing service status and useful URLs |
| `GET` | `/favicon.ico` | Returns HTTP 204 to avoid a missing-favicon error |
| Various | `/admin/` | Standard Django administration site |
| `GET` | `/media/<path>` | Serves uploaded/generated runtime files in development mode |

### `GET /api/health/`

Purpose: simple backend connectivity/health check.

Response: `status`, service name, and a database-connected label. Note that the current view returns this label without executing a dedicated database probe.

### `GET /api/dashboard/`

Purpose: aggregate application history for a dashboard.

It returns total datasets, total runs, completed-run count, and the eight most recent runs with dataset name, status, problem type, and creation time. The current React dashboard does not call it yet.

### `POST /api/datasets/upload/`

Purpose: validate, store, and preview a CSV.

Input: multipart form field `file`. Success is HTTP 201 with dataset ID, name, dimensions, columns, and up to ten preview rows. Common validation errors are missing file, wrong extension, file over 10 MB, unreadable CSV, empty data, or fewer than two columns.

### `POST /api/runs/start/`

Purpose: create an AutoML run and launch it asynchronously in a background thread.

Input fields:

- `dataset_id` — required existing dataset UUID;
- `target_column` — optional; defaults to the dataset’s last column;
- `mode` — optional `auto` or `guided`, default `auto`.

Success is HTTP 202 with the run ID, target and reason, problem type, algorithms, and pending status. Runtime failures are stored and exposed by the status endpoint. Invalid target, mode, or algorithms return HTTP 400.

### `GET /api/runs/{run_id}/status/`

Purpose: expose current/persisted execution state.

It returns run ID, status (`pending`, `running`, `completed`, or `failed`), numeric progress, current agent, chronological log objects, and safe error text. The progress page polls it every 1.2 seconds until completion/failure.

### `GET /api/runs/{run_id}/results/`

Purpose: return the complete report/result JSON stored on the `Run` record.

It is available only when the run is completed. Otherwise it returns HTTP 409 with code `results_not_ready`. Results cover dataset profiling, routing, preprocessing, training, explainability, target, leaderboard, best model, and model ID.

### `GET /api/runs/{run_id}/artifacts/`

Purpose: list downloadable generated files for a run.

Each item has database ID, display name, kind, and an absolute media URL. A cleaned CSV exists only if CleanCraft ran; the JSON report is produced for successful runs.

### `GET /api/models/{model_id}/predict/`

Purpose: retrieve the input contract needed to make predictions.

It returns model ID/name, ordered feature schema (`name` and `number`/`text` type), target column, and problem type. The frontend uses it to generate the form dynamically.

### `POST /api/models/{model_id}/predict/`

Purpose: make one prediction with a saved model pipeline.

Preferred body:

```json
{
  "features": {
    "feature_one": 12.5,
    "feature_two": "category A"
  }
}
```

The endpoint also accepts feature keys directly at the top level. It rejects missing required fields, converts numeric/text types, loads the `.joblib` pipeline, predicts one Pandas row, reverses target label encoding when applicable, and returns `prediction`, model name, and target name.

All application validation errors generally use:

```json
{
  "error": {
    "code": "validation_error",
    "message": "Human-readable explanation"
  }
}
```

## 7. Frontend routes and their purpose

| React route | Page | Backend calls |
| --- | --- | --- |
| `/` | Static landing/dashboard | None currently |
| `/upload` | Upload, preview, target/mode selection | Upload; start run |
| `/runs/:runId/progress` | Progress, current agent, logs, errors | Run status |
| `/runs/:runId/results` | Routing, leaderboard, explanations | Run results |
| `/runs/:runId/visualizations` | Quality charts, model comparison, correlation heatmap | Run results |
| `/runs/:runId/report` | Summary and downloads | Results + artifacts |
| `/predict/:modelId` | Schema-built form and prediction | GET + POST predict |
| any unmatched route | Not-found page | None |

`frontend/src/lib/api.js` centralizes the network behavior. It parses JSON, turns non-2xx backend responses into JavaScript errors, and exposes `upload`, `startRun`, `status`, `results`, `artifacts`, `modelSchema`, and `predict` functions.

## 8. What `db.sqlite3` does

`backend/db.sqlite3` is the local relational database used by Django. It stores durable **structured metadata and state**, not the large file contents themselves.

### Application tables

#### `Dataset`

Stores the dataset UUID, original filename, relative file path, row/column counts, column-name JSON, preview JSON, and upload time. The CSV bytes are on disk in `runtime/datasets/`.

#### `Run`

Stores the selected dataset relationship, target, mode, inferred problem type, execution status/progress/current agent, log JSON, final result JSON, errors, and timestamps. Deleting a dataset cascades to its runs.

#### `TrainedModel`

Stores one selected model per run, model UUID/name, relative Joblib path, required feature-schema JSON, and creation time. The actual serialized model is under `runtime/models/`.

#### `Artifact`

Stores a run relationship, artifact kind/name, relative file path, and creation time. The actual report/CSV is under `runtime/artifacts/<run UUID>/`.

SQLite also contains Django’s standard migration, authentication, session, content-type, and admin tables.

### Database versus runtime files

```text
db.sqlite3
├── knows dataset/run/model/artifact IDs
├── stores status, logs, results, preview, schema, and relationships
└── stores relative references to files

runtime/
├── datasets/   → uploaded CSV bytes
├── models/     → trained Joblib preprocessing + model pipelines
└── artifacts/  → cleaned CSVs and report JSON files
```

Both are required for a fully working saved run. Copying only SQLite loses uploaded/model/artifact files; copying only `runtime/` loses IDs, relationships, schemas, results, and lookup state. Django migrations create/update database tables; run `python manage.py migrate` when setting up the backend.

## 9. Persistence and failure behavior

Successful execution leaves:

- one `Dataset` record and uploaded CSV;
- one `Run` record with completed state, logs, and report JSON;
- one `TrainedModel` record and `.joblib` file;
- a report `Artifact`, plus a cleaned-dataset `Artifact` when CleanCraft ran.

If an agent raises an exception, `AgentWorkflow` changes the run to `failed`, stores the exception text, appends a final failure log, and the start endpoint returns HTTP 422. Partial records/files created before the failure may remain.

## 10. Current limitations and practical observations

- Workflow execution uses an in-process daemon thread. It supports live local progress, but a server restart can interrupt a job; production should use a durable queue.
- Guided mode controls target and algorithms before launch but has no intermediate pause/resume steps.
- Agents are named modular stages, not independently deployed or LLM-powered agents.
- SQLite is appropriate for local development and a capstone demo, but a production multi-user deployment would normally use a production database and separate object storage.
- Django serves `/media/` through its development helper; production needs a proper media server/storage configuration.
- There is no authentication or per-user ownership, so all stored runs are application-global.
- `/api/dashboard/` is implemented but not connected to the current landing page.
- The health response labels the database connected but does not perform an explicit query.
- Prediction accepts one row per request; there is no batch prediction endpoint.
- Uploaded files and generated models can consume disk space; no cleanup/retention endpoint exists.

## 11. Running the project locally

Backend:

```powershell
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Frontend in a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Then open `http://localhost:5173`. Run backend tests with `python manage.py test automl`, and frontend checks with `npm run lint` and `npm run build`.

## 12. One-sentence mental model

The React frontend collects a CSV and configuration, Django records them in SQLite, one synchronous Python `AgentWorkflow` profiles/routes/cleans/trains/explains the data, large outputs are saved under `runtime/`, and later API requests retrieve the stored state, downloadable artifacts, or trained pipeline for prediction.
