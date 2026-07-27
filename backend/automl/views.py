import pandas as pd
import threading
from django.db import close_old_connections, transaction
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Dataset, Run, TrainedModel
from .pipeline import ALGORITHM_CATALOG, AgentWorkflow, _json_value, infer_problem_type, recommend_target


def error(message, code="validation_error", http=status.HTTP_400_BAD_REQUEST):
    return Response({"error": {"code": code, "message": str(message)}}, status=http)


@api_view(["GET"])
def health(request):
    return Response({"status": "ok", "service": "DataPilot AI", "database": "connected"})


@api_view(["GET"])
def dashboard(request):
    recent = Run.objects.select_related("dataset").order_by("-created_at")[:8]
    return Response({
        "datasets": Dataset.objects.count(),
        "runs": Run.objects.count(),
        "completed_runs": Run.objects.filter(status="completed").count(),
        "recent_runs": [{
            "id": str(run.id), "dataset": run.dataset.name, "status": run.status,
            "problem_type": run.problem_type, "created_at": run.created_at,
        } for run in recent],
    })


@api_view(["POST"])
def upload_dataset(request):
    upload = request.FILES.get("file")
    if not upload:
        return error("A CSV file is required.")
    if not upload.name.lower().endswith(".csv"):
        return error("Only CSV files are supported.")
    if upload.size > 10 * 1024 * 1024:
        return error("The maximum file size is 10 MB.")
    try:
        frame = pd.read_csv(upload)
    except Exception as exc:
        return error(f"The CSV could not be read: {exc}")
    if frame.empty or len(frame.columns) < 2:
        return error("The dataset must contain rows and at least two columns.")
    upload.seek(0)
    preview = [{str(k): _json_value(v) for k, v in row.items()} for row in frame.head(10).to_dict("records")]
    dataset = Dataset.objects.create(
        name=upload.name, file=upload, rows=len(frame), columns=len(frame.columns),
        column_names=[str(c) for c in frame.columns], preview=preview,
    )
    recommendation = recommend_target(frame)
    target_options = {str(column): infer_problem_type(frame[column].dropna())["problem_type"] for column in frame.columns}
    return Response({
        "id": str(dataset.id), "name": dataset.name, "rows": dataset.rows, "columns": dataset.columns,
        "column_names": dataset.column_names, "preview": dataset.preview,
        "target_recommendation": recommendation, "target_options": target_options,
        "algorithm_catalog": ALGORITHM_CATALOG,
    }, status=status.HTTP_201_CREATED)


def _execute_run(run_id):
    close_old_connections()
    try:
        AgentWorkflow(Run.objects.select_related("dataset").get(pk=run_id)).execute()
    except Exception:
        pass
    finally:
        close_old_connections()


def _launch_run(run_id):
    threading.Thread(target=_execute_run, args=(run_id,), daemon=True, name=f"datapilot-{run_id}").start()


@api_view(["POST"])
def start_run(request):
    dataset = get_object_or_404(Dataset, pk=request.data.get("dataset_id"))
    mode = request.data.get("mode", "auto")
    if mode not in {"auto", "guided"}:
        return error("Mode must be 'auto' or 'guided'.")
    frame = pd.read_csv(dataset.file.path)
    recommendation = recommend_target(frame)
    target = recommendation["column"] if mode == "auto" else request.data.get("target_column")
    if mode == "guided" and not target:
        return error("Guided mode requires a target column.")
    if target not in dataset.column_names:
        return error("The selected target column is invalid.")
    problem_type = infer_problem_type(frame[target].dropna())["problem_type"]
    allowed = ALGORITHM_CATALOG[problem_type]
    requested = request.data.get("algorithms", []) if mode == "guided" else allowed
    selected = list(dict.fromkeys(requested or allowed))
    invalid = [name for name in selected if name not in allowed]
    if invalid:
        return error(f"Unsupported {problem_type} algorithms: {', '.join(invalid)}")
    reason = recommendation["reason"] if mode == "auto" else "Selected explicitly by the user in Guided mode."
    run = Run.objects.create(dataset=dataset, target_column=target, target_selection_reason=reason,
                             selected_algorithms=selected, mode=mode, problem_type=problem_type)
    transaction.on_commit(lambda: _launch_run(run.id))
    return Response({"run_id": str(run.id), "status": run.status, "target_column": target,
                     "target_selection_reason": reason, "problem_type": problem_type,
                     "selected_algorithms": selected}, status=status.HTTP_202_ACCEPTED)


@api_view(["GET"])
def run_status(request, run_id):
    run = get_object_or_404(Run, pk=run_id)
    ranges = {"PilotFlow": (0, 24), "DataLens": (0, 12), "CleanCraft": (24, 50), "ModelForge": (36, 78), "InsightBoard": (78, 100)}
    start, finish = ranges.get(run.current_agent, (0, 100))
    agent_progress = 100 if run.status == "completed" else max(0, min(99, round((run.progress - start) / max(1, finish - start) * 100)))
    return Response({
        "id": str(run.id), "status": run.status, "progress": run.progress,
        "current_agent": run.current_agent, "logs": run.logs, "error": run.error,
        "mode": run.mode, "target_column": run.target_column,
        "target_selection_reason": run.target_selection_reason,
        "selected_algorithms": run.selected_algorithms,
        "agent_progress": agent_progress,
    })


@api_view(["GET"])
def run_results(request, run_id):
    run = get_object_or_404(Run, pk=run_id)
    if run.status != "completed":
        return error("Results are not ready.", "results_not_ready", status.HTTP_409_CONFLICT)
    return Response(run.results)


@api_view(["GET"])
def run_artifacts(request, run_id):
    run = get_object_or_404(Run, pk=run_id)
    return Response({"artifacts": [{
        "id": artifact.id, "name": artifact.name, "kind": artifact.kind,
        "url": request.build_absolute_uri(artifact.file.url),
    } for artifact in run.artifacts.all()]})


@api_view(["GET", "POST"])
def predict(request, model_id):
    model = get_object_or_404(TrainedModel, pk=model_id)
    if request.method == "GET":
        return Response({"id": str(model.id), "name": model.name, "features": model.feature_schema,
                         "target": model.run.target_column, "problem_type": model.run.problem_type})
    values = request.data.get("features", request.data)
    missing = [item["name"] for item in model.feature_schema if item["name"] not in values]
    if missing:
        return error(f"Missing required features: {', '.join(missing)}")
    try:
        row = {}
        for item in model.feature_schema:
            value = values[item["name"]]
            row[item["name"]] = float(value) if item["type"] == "number" else str(value)
        payload = __import__("joblib").load(model.artifact.path)
        prediction = payload["pipeline"].predict(pd.DataFrame([row]))[0]
        if payload["target_encoder"] is not None:
            prediction = payload["target_encoder"].inverse_transform([int(prediction)])[0]
        prediction = _json_value(prediction)
    except Exception as exc:
        return error(f"Prediction failed: {exc}")
    return Response({"prediction": prediction, "model": model.name, "target": model.run.target_column})
