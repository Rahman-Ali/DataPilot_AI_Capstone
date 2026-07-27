# import json
# from datetime import datetime, timezone
# from pathlib import Path

# import joblib
# import numpy as np
# import pandas as pd
# from django.conf import settings
# from django.core.files import File
# from sklearn.compose import ColumnTransformer
# from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, GradientBoostingClassifier, GradientBoostingRegressor
# from sklearn.impute import SimpleImputer
# from sklearn.inspection import permutation_importance
# from sklearn.linear_model import LogisticRegression, Ridge
# from sklearn.metrics import accuracy_score, f1_score, mean_absolute_error, mean_squared_error, r2_score
# from sklearn.model_selection import train_test_split
# from sklearn.pipeline import Pipeline
# from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler

# from .models import Artifact, Run, TrainedModel


# def _json_value(value):
#     if pd.isna(value):
#         return None
#     if isinstance(value, (np.integer,)):
#         return int(value)
#     if isinstance(value, (np.floating,)):
#         return float(value)
#     return value


# class AgentWorkflow:
#     """Deterministic five-agent workflow. Agent decisions are persisted for the UI."""

#     def __init__(self, run: Run):
#         self.run = run
#         self.df = pd.read_csv(run.dataset.file.path)
#         self.target = run.target_column

#     def log(self, agent, message, progress):
#         self.run.current_agent = agent
#         self.run.progress = progress
#         logs = list(self.run.logs)
#         logs.append({"time": datetime.now(timezone.utc).isoformat(), "agent": agent, "message": message})
#         self.run.logs = logs
#         self.run.save(update_fields=["current_agent", "progress", "logs", "updated_at"])

#     def execute(self):
#         self.run.status = "running"
#         self.run.save(update_fields=["status", "updated_at"])
#         try:
#             profile = self.data_lens()
#             route = self.pilot_flow(profile)
#             preprocessing = self.clean_craft(route)
#             training = self.model_forge(preprocessing)
#             results = self.insight_board(profile, preprocessing, training, route)
#             self.run.results = results
#             self.run.status = "completed"
#             self.run.progress = 100
#             self.run.current_agent = "InsightBoard"
#             self.run.save()
#         except Exception as exc:
#             self.run.status = "failed"
#             self.run.error = str(exc)
#             self.run.logs = [*self.run.logs, {
#                 "time": datetime.now(timezone.utc).isoformat(),
#                 "agent": self.run.current_agent,
#                 "message": f"Workflow stopped: {exc}",
#             }]
#             self.run.save()
#             raise

#     def data_lens(self):
#         self.log("DataLens", "Inspecting dataset structure and quality", 15)
#         if self.target not in self.df.columns:
#             raise ValueError(f"Target column '{self.target}' does not exist.")
#         if len(self.df) < 20:
#             raise ValueError("At least 20 rows are required for a reliable train/test split.")
#         y = self.df[self.target]
#         unique = y.nunique(dropna=True)
#         numeric_target = pd.api.types.is_numeric_dtype(y)
#         problem_type = "classification" if (not numeric_target or unique <= max(20, int(len(y) * 0.05))) else "regression"
#         self.run.problem_type = problem_type
#         self.run.save(update_fields=["problem_type", "updated_at"])
#         return {
#             "rows": len(self.df),
#             "columns": len(self.df.columns),
#             "missing_values": int(self.df.isna().sum().sum()),
#             "duplicate_rows": int(self.df.duplicated().sum()),
#             "categorical_columns": [c for c in self.df.columns if not pd.api.types.is_numeric_dtype(self.df[c])],
#             "numeric_columns": [c for c in self.df.columns if pd.api.types.is_numeric_dtype(self.df[c])],
#             "problem_type": problem_type,
#             "target_unique_values": int(unique),
#         }

#     def pilot_flow(self, profile):
#         features = self.df.drop(columns=[self.target])
#         reasons = []
#         if features.isna().any().any() or self.df[self.target].isna().any():
#             reasons.append("missing values")
#         if self.df.duplicated().any():
#             reasons.append("duplicate rows")
#         if any(not pd.api.types.is_numeric_dtype(features[c]) for c in features):
#             reasons.append("categorical features")
#         needs_cleaning = bool(reasons)
#         destination = "CleanCraft" if needs_cleaning else "ModelForge"
#         detail = ", ".join(reasons) if reasons else "dataset is already numeric, complete, and duplicate-free"
#         self.log("PilotFlow", f"Decision: route to {destination}; {detail}", 25)
#         return {"needs_cleaning": needs_cleaning, "destination": destination, "reasons": reasons}

#     def clean_craft(self, route):
#         df = self.df.drop_duplicates().copy()
#         df = df[df[self.target].notna()]
#         X = df.drop(columns=[self.target])
#         y = df[self.target]
#         numeric = list(X.select_dtypes(include=np.number).columns)
#         categorical = [c for c in X.columns if c not in numeric]
#         if route["needs_cleaning"]:
#             self.log("CleanCraft", "Handling missing values, encoding categories, and scaling numeric features", 40)
#         else:
#             self.log("CleanCraft", "Bypassed: PilotFlow confirmed no data preparation was required", 40)
#         numeric_steps = Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())])
#         categorical_steps = Pipeline([
#             ("imputer", SimpleImputer(strategy="most_frequent")),
#             ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
#         ])
#         transformer = ColumnTransformer([
#             ("numeric", numeric_steps, numeric),
#             ("categorical", categorical_steps, categorical),
#         ], remainder="drop")
#         target_encoder = None
#         if self.run.problem_type == "classification" and not pd.api.types.is_numeric_dtype(y):
#             target_encoder = LabelEncoder()
#             y = target_encoder.fit_transform(y.astype(str))
#         cleaned = df.copy()
#         for col in numeric:
#             cleaned[col] = cleaned[col].fillna(cleaned[col].median())
#         for col in categorical:
#             mode = cleaned[col].mode(dropna=True)
#             cleaned[col] = cleaned[col].fillna(mode.iloc[0] if len(mode) else "Unknown")
#         self._save_dataframe(cleaned, "cleaned_dataset.csv", "cleaned_dataset")
#         schema = [{"name": c, "type": "number" if c in numeric else "text"} for c in X.columns]
#         return {"X": X, "y": y, "transformer": transformer, "target_encoder": target_encoder, "schema": schema,
#                 "numeric": numeric, "categorical": categorical, "rows_after_cleaning": len(df)}

#     def model_forge(self, prep):
#         self.log("ModelForge", f"Training candidate {self.run.problem_type} algorithms", 55)
#         stratify = prep["y"] if self.run.problem_type == "classification" and len(np.unique(prep["y"])) > 1 else None
#         X_train, X_test, y_train, y_test = train_test_split(
#             prep["X"], prep["y"], test_size=0.2, random_state=42, stratify=stratify
#         )
#         if self.run.problem_type == "classification":
#             models = {
#                 "Logistic Regression": LogisticRegression(max_iter=1000),
#                 "Random Forest": RandomForestClassifier(n_estimators=120, random_state=42),
#                 "Gradient Boosting": GradientBoostingClassifier(random_state=42),
#             }
#         else:
#             models = {
#                 "Ridge Regression": Ridge(),
#                 "Random Forest": RandomForestRegressor(n_estimators=120, random_state=42),
#                 "Gradient Boosting": GradientBoostingRegressor(random_state=42),
#             }
#         leaderboard, fitted = [], {}
#         for name, estimator in models.items():
#             pipe = Pipeline([("preprocessor", prep["transformer"]), ("model", estimator)])
#             pipe.fit(X_train, y_train)
#             prediction = pipe.predict(X_test)
#             if self.run.problem_type == "classification":
#                 metrics = {"accuracy": accuracy_score(y_test, prediction), "f1": f1_score(y_test, prediction, average="weighted", zero_division=0)}
#                 score = metrics["f1"]
#             else:
#                 metrics = {"r2": r2_score(y_test, prediction), "mae": mean_absolute_error(y_test, prediction),
#                            "rmse": mean_squared_error(y_test, prediction) ** 0.5}
#                 score = metrics["r2"]
#             leaderboard.append({"model": name, **{k: round(float(v), 5) for k, v in metrics.items()}, "score": round(float(score), 5)})
#             fitted[name] = pipe
#         leaderboard.sort(key=lambda item: item["score"], reverse=True)
#         best_name = leaderboard[0]["model"]
#         best = fitted[best_name]
#         model_dir = Path(settings.MEDIA_ROOT) / "models"
#         model_dir.mkdir(parents=True, exist_ok=True)
#         path = model_dir / f"{self.run.id}.joblib"
#         joblib.dump({"pipeline": best, "target_encoder": prep["target_encoder"], "target": self.target}, path)
#         with path.open("rb") as handle:
#             saved = TrainedModel(run=self.run, name=best_name, feature_schema=prep["schema"])
#             saved.artifact.save(path.name, File(handle), save=True)
#         self.log("ModelForge", f"Compared three models; selected {best_name}", 78)
#         return {"leaderboard": leaderboard, "best_name": best_name, "pipeline": best, "X_test": X_test,
#                 "y_test": y_test, "model_id": str(saved.id)}

#     def insight_board(self, profile, prep, training, route):
#         self.log("InsightBoard", "Calculating explainable feature contributions and preparing report", 88)
#         importance = permutation_importance(
#             training["pipeline"], training["X_test"], training["y_test"],
#             n_repeats=5, random_state=42,
#             scoring="f1_weighted" if self.run.problem_type == "classification" else "r2",
#         )
#         contributions = sorted([
#             {"feature": name, "importance": round(max(0.0, float(value)), 6)}
#             for name, value in zip(training["X_test"].columns, importance.importances_mean)
#         ], key=lambda x: x["importance"], reverse=True)
#         explanation_method = "permutation importance (model-agnostic XAI)"
#         try:
#             contributions = self._lime_contributions(prep, training) or contributions
#             explanation_method = "LIME"
#         except Exception:
#             pass
#         summary = (
#             f"PilotFlow identified a {profile['problem_type']} problem and "
#             f"{'sent the dataset through CleanCraft' if route['needs_cleaning'] else 'sent the model-ready dataset directly to ModelForge'}. "
#             f"{training['best_name']} achieved the strongest validation score."
#         )
#         report = {
#             "summary": summary, "dataset": profile, "routing": route,
#             "preprocessing": {
#                 "applied": route["needs_cleaning"], "numeric_columns": prep["numeric"],
#                 "categorical_columns": prep["categorical"], "rows_after_cleaning": prep["rows_after_cleaning"],
#             },
#             "leaderboard": training["leaderboard"], "best_model": training["best_name"],
#             "model_id": training["model_id"], "explanation_method": explanation_method,
#             "feature_contributions": contributions, "target_column": self.target,
#         }
#         self._save_report(report)
#         self.log("InsightBoard", "Results, explanations, and downloadable artifacts are ready", 100)
#         return report

#     def _lime_contributions(self, prep, training):
#         transformer = training["pipeline"].named_steps["preprocessor"]
#         estimator = training["pipeline"].named_steps["model"]
#         transformed = np.asarray(transformer.transform(training["X_test"]), dtype=float)
#         names = list(transformer.get_feature_names_out())
#         rng = np.random.default_rng(42)
#         scale = np.std(transformed, axis=0)
#         scale[scale == 0] = 1
#         totals = np.zeros(transformed.shape[1])
#         count = min(5, len(transformed))
#         # LIME: perturb each observation, weight samples by locality, and fit a
#         # sparse-friendly linear surrogate whose coefficients explain that point.
#         for row in transformed[:count]:
#             samples = row + rng.normal(size=(500, len(row))) * scale * 0.35
#             distances = np.linalg.norm((samples - row) / scale, axis=1)
#             weights = np.exp(-(distances ** 2) / max(1, len(row) * 0.75))
#             if self.run.problem_type == "classification":
#                 probabilities = estimator.predict_proba(samples)
#                 predicted_class = int(estimator.predict(row.reshape(1, -1))[0])
#                 outcomes = probabilities[:, list(estimator.classes_).index(predicted_class)]
#             else:
#                 outcomes = estimator.predict(samples)
#             surrogate = Ridge(alpha=1.0)
#             surrogate.fit(samples, outcomes, sample_weight=weights)
#             totals += np.abs(surrogate.coef_ * scale)
#         grouped = {}
#         for name, value in zip(names, totals / count):
#             clean = name.split("__", 1)[-1]
#             original = next((column for column in prep["schema"] if clean == column["name"] or clean.startswith(f"{column['name']}_")), None)
#             key = original["name"] if original else clean
#             grouped[key] = grouped.get(key, 0) + float(value)
#         return [{"feature": key, "importance": round(value, 6)}
#                 for key, value in sorted(grouped.items(), key=lambda item: item[1], reverse=True)]

#     def _save_dataframe(self, frame, name, kind):
#         folder = Path(settings.MEDIA_ROOT) / "artifacts" / str(self.run.id)
#         folder.mkdir(parents=True, exist_ok=True)
#         path = folder / name
#         frame.to_csv(path, index=False)
#         with path.open("rb") as handle:
#             artifact = Artifact(run=self.run, kind=kind, name=name)
#             artifact.file.save(f"{self.run.id}/{name}", File(handle), save=True)

#     def _save_report(self, report):
#         folder = Path(settings.MEDIA_ROOT) / "artifacts" / str(self.run.id)
#         folder.mkdir(parents=True, exist_ok=True)
#         path = folder / "report.json"
#         path.write_text(json.dumps(report, indent=2), encoding="utf-8")
#         with path.open("rb") as handle:
#             artifact = Artifact(run=self.run, kind="report", name="report.json")
#             artifact.file.save(f"{self.run.id}/report.json", File(handle), save=True)
"""DataPilot AI multi-agent AutoML workflow.

Agents
------
PilotFlow   : Orchestrates and routes the workflow.
DataLens    : Profiles data, validates the target, and infers the ML problem.
CleanCraft  : Applies corrective cleaning only when DataLens identifies a need.
ModelForge  : Builds leakage-safe pipelines, tunes several algorithms, and selects a model.
InsightBoard: Produces metrics, statistics, model-agnostic XAI, and artifacts.
"""

from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from django.conf import settings
from django.core.files import File
from sklearn.base import BaseEstimator
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import (
    GradientBoostingClassifier,
    GradientBoostingRegressor,
    RandomForestClassifier,
    RandomForestRegressor,
)
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
)
from sklearn.model_selection import (
    KFold,
    RandomizedSearchCV,
    StratifiedKFold,
    train_test_split,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler

from .models import Artifact, Run, TrainedModel


RANDOM_STATE = 42
TEST_SIZE = 0.20
MAX_SEARCH_ITERATIONS = 6

ALGORITHM_CATALOG = {
    "classification": ["Logistic Regression", "Random Forest", "Gradient Boosting"],
    "regression": ["Ridge Regression", "Random Forest", "Gradient Boosting"],
}


def infer_problem_type(target: pd.Series) -> dict[str, Any]:
    unique = int(target.nunique(dropna=True))
    numeric = pd.api.types.is_numeric_dtype(target)
    rows = len(target)
    if not numeric:
        return {"problem_type": "classification", "subtype": "binary" if unique == 2 else "multiclass", "confidence": 0.98, "reasons": ["target is non-numeric"]}
    if pd.api.types.is_bool_dtype(target) or unique <= 2:
        return {"problem_type": "classification", "subtype": "binary", "confidence": 0.99, "reasons": ["target has two unique values"]}
    if unique <= min(20, max(3, int(rows * 0.05))):
        return {"problem_type": "classification", "subtype": "multiclass", "confidence": 0.80, "reasons": ["numeric target has low cardinality"]}
    return {"problem_type": "regression", "subtype": "continuous", "confidence": 0.88, "reasons": ["numeric target has continuous/high-cardinality values"]}


def recommend_target(frame: pd.DataFrame) -> dict[str, Any]:
    """Choose a plausible target using transparent deterministic heuristics."""
    signals = ("target", "label", "outcome", "class", "churn", "price", "sales", "score", "risk", "status")
    ranked = []
    rows = max(1, len(frame))
    for position, column in enumerate(frame.columns):
        series = frame[column]
        lower = str(column).lower().strip()
        unique = int(series.nunique(dropna=True))
        matches = [signal for signal in signals if signal in lower]
        identifier = lower == "id" or lower.endswith("_id") or "uuid" in lower
        score = (60 if matches else 0) + position / max(1, len(frame.columns) - 1) * 12
        score += 10 if 2 <= unique < rows else 0
        score -= 100 if identifier else 0
        score -= 35 if unique / rows >= 0.98 and not pd.api.types.is_numeric_dtype(series) else 0
        score -= float(series.isna().mean()) * 30
        ranked.append((score, str(column), matches, unique, float(series.isna().mean())))
    _, column, matches, unique, missing_ratio = max(ranked)
    reasons = []
    if matches:
        reasons.append(f"its name contains the outcome signal '{matches[0]}'")
    if column == str(frame.columns[-1]):
        reasons.append("it is the final column, a common label convention")
    reasons.append(f"it has {unique} distinct non-null values across {rows} rows")
    if missing_ratio == 0:
        reasons.append("it has no missing values")
    return {"column": column, "reason": "Selected because " + "; ".join(reasons) + ".", "method": "name, position, cardinality, identifier, and completeness scoring"}


def _json_value(value: Any) -> Any:
    """Convert NumPy/Pandas values into JSON-safe Python values."""
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value)
    if isinstance(value, np.bool_):
        return bool(value)
    return value


def _finite_or_none(value: float) -> float | None:
    value = float(value)
    return value if math.isfinite(value) else None


class AgentWorkflow:
    """Rule-based multi-agent AutoML workflow with persisted routing decisions."""

    def __init__(self, run: Run):
        self.run = run
        self.df = pd.read_csv(run.dataset.file.path)
        self.target = run.target_column

    # ------------------------------------------------------------------
    # Workflow orchestration
    # ------------------------------------------------------------------
    def log(self, agent: str, message: str, progress: int) -> None:
        self.run.current_agent = agent
        self.run.progress = progress
        logs = list(self.run.logs or [])
        logs.append(
            {
                "time": datetime.now(timezone.utc).isoformat(),
                "agent": agent,
                "message": message,
            }
        )
        self.run.logs = logs
        self.run.save(
            update_fields=["current_agent", "progress", "logs", "updated_at"]
        )

    def execute(self) -> dict[str, Any]:
        """Execute agents using real conditional routing."""
        self.run.status = "running"
        self.run.error = ""
        self.run.save(update_fields=["status", "error", "updated_at"])

        try:
            profile = self.data_lens()
            route = self.pilot_flow(profile)

            if route["blocking_issues"]:
                raise ValueError("; ".join(route["blocking_issues"]))

            if route["needs_corrective_cleaning"]:
                prepared = self.clean_craft(profile, route)
            else:
                prepared = self.prepare_model_ready_data(profile)

            training = self.model_forge(prepared)
            results = self.insight_board(profile, prepared, training, route)

            self.run.results = results
            self.run.status = "completed"
            self.run.progress = 100
            self.run.current_agent = "InsightBoard"
            self.run.save()
            return results

        except Exception as exc:
            self._handle_failure(exc)
            raise

    # ------------------------------------------------------------------
    # DataLens Agent
    # ------------------------------------------------------------------
    def data_lens(self) -> dict[str, Any]:
        self.log("DataLens", "Profiling dataset structure, quality, and target", 12)

        if self.target not in self.df.columns:
            raise ValueError(f"Target column '{self.target}' does not exist.")
        if len(self.df) < 20:
            raise ValueError("At least 20 rows are required for model training.")
        if len(self.df.columns) < 2:
            raise ValueError("The dataset must contain at least one feature and one target.")

        features = self.df.drop(columns=[self.target])
        target = self.df[self.target]
        non_null_target = target.dropna()

        if non_null_target.empty:
            raise ValueError("The target column contains no usable values.")

        problem = infer_problem_type(non_null_target)
        self.run.problem_type = problem["problem_type"]
        self.run.save(update_fields=["problem_type", "updated_at"])

        numeric = list(features.select_dtypes(include=np.number).columns)
        categorical = [column for column in features.columns if column not in numeric]
        constant = [column for column in features.columns if features[column].nunique(dropna=True) <= 1]
        identifier_like = self._identifier_like_columns(features)
        infinite_counts = {
            column: int(np.isinf(pd.to_numeric(features[column], errors="coerce")).sum())
            for column in numeric
        }
        total_infinite = int(sum(infinite_counts.values()))
        high_cardinality = [
            column
            for column in categorical
            if features[column].nunique(dropna=True) > max(50, int(len(features) * 0.50))
        ]
        scale_profile = self._detect_scaling_need(features[numeric])
        outlier_profile = self._detect_outliers(features[numeric])

        class_distribution: dict[str, int] | None = None
        class_imbalance_ratio: float | None = None
        if problem["problem_type"] == "classification":
            counts = non_null_target.astype(str).value_counts()
            class_distribution = {str(key): int(value) for key, value in counts.items()}
            if len(counts) > 1 and counts.min() > 0:
                class_imbalance_ratio = round(float(counts.max() / counts.min()), 4)

        statistics = self._basic_statistics(features)

        return {
            "rows": int(len(self.df)),
            "columns": int(len(self.df.columns)),
            "feature_columns": int(features.shape[1]),
            "missing_values": int(self.df.isna().sum().sum()),
            "missing_by_column": {
                column: int(value)
                for column, value in self.df.isna().sum().items()
                if int(value) > 0
            },
            "duplicate_rows": int(self.df.duplicated().sum()),
            "infinite_values": total_infinite,
            "infinite_by_column": {k: v for k, v in infinite_counts.items() if v > 0},
            "categorical_columns": categorical,
            "numeric_columns": numeric,
            "constant_columns": constant,
            "identifier_like_columns": identifier_like,
            "high_cardinality_columns": high_cardinality,
            "problem_type": problem["problem_type"],
            "problem_subtype": problem["subtype"],
            "problem_confidence": problem["confidence"],
            "problem_reasons": problem["reasons"],
            "target_unique_values": int(non_null_target.nunique()),
            "target_missing_values": int(target.isna().sum()),
            "class_distribution": class_distribution,
            "class_imbalance_ratio": class_imbalance_ratio,
            "scaling": scale_profile,
            "outliers": outlier_profile,
            "statistics": statistics,
            "data_quality": {
                "completeness": round(float((1 - self.df.isna().sum().sum() / max(1, self.df.size)) * 100), 2),
                "uniqueness": round(float((1 - self.df.duplicated().sum() / max(1, len(self.df))) * 100), 2),
                "validity": round(float((1 - total_infinite / max(1, features.size)) * 100), 2),
            },
            "correlation_matrix": self._correlation_matrix(features),
        }

    # ------------------------------------------------------------------
    # PilotFlow Agent
    # ------------------------------------------------------------------
    def pilot_flow(self, profile: dict[str, Any]) -> dict[str, Any]:
        reasons: list[str] = []
        warnings: list[str] = []
        blocking: list[str] = []

        if profile["target_missing_values"]:
            reasons.append("missing target values")
        if profile["missing_values"] - profile["target_missing_values"] > 0:
            reasons.append("missing feature values")
        if profile["duplicate_rows"]:
            reasons.append("duplicate rows")
        if profile["infinite_values"]:
            reasons.append("infinite numeric values")
        if profile["constant_columns"]:
            reasons.append("constant features")

        if profile["categorical_columns"]:
            warnings.append("categorical features require model-pipeline encoding")
        if profile["scaling"]["needs_scaling"]:
            warnings.append("numeric features have materially different scales")
        if profile["high_cardinality_columns"]:
            warnings.append("high-cardinality categorical features detected")
        if profile["identifier_like_columns"]:
            warnings.append("possible identifier columns detected")
        if profile["outliers"]["columns_with_outliers"]:
            warnings.append("possible numeric outliers detected")

        if profile["feature_columns"] == 0:
            blocking.append("No feature columns remain after selecting the target")
        if profile["problem_type"] == "classification":
            class_count = profile["target_unique_values"]
            if class_count < 2:
                blocking.append("Classification requires at least two target classes")
            distribution = profile.get("class_distribution") or {}
            if distribution and min(distribution.values()) < 2:
                blocking.append("Every target class needs at least two samples")
            if profile.get("class_imbalance_ratio") and profile["class_imbalance_ratio"] >= 10:
                warnings.append("severe target class imbalance detected")

        needs_cleaning = bool(reasons)
        destination = "CleanCraft" if needs_cleaning else "ModelForge"
        detail = ", ".join(reasons) if reasons else "no corrective cleaning is required"
        self.log("PilotFlow", f"Route selected: {destination}; {detail}", 24)

        return {
            "needs_corrective_cleaning": needs_cleaning,
            "needs_cleaning": needs_cleaning,
            "destination": destination,
            "reasons": reasons,
            "warnings": warnings,
            "blocking_issues": blocking,
            "model_pipeline_transformations": {
                "imputation": True,
                "categorical_encoding": bool(profile["categorical_columns"]),
                "numeric_scaling": True,
            },
        }

    # ------------------------------------------------------------------
    # CleanCraft Agent and preparation services
    # ------------------------------------------------------------------
    def clean_craft(
        self,
        profile: dict[str, Any],
        route: dict[str, Any],
    ) -> dict[str, Any]:
        self.log(
            "CleanCraft",
            "Applying corrective cleaning while preserving train-time transformations",
            36,
        )

        cleaned = self.df.copy()
        cleaned = cleaned.replace([np.inf, -np.inf], np.nan)
        cleaned = cleaned.drop_duplicates()
        cleaned = cleaned[cleaned[self.target].notna()].copy()

        # Constant columns contain no predictive information.
        removable_constants = [
            column for column in profile["constant_columns"] if column != self.target
        ]
        if removable_constants:
            cleaned = cleaned.drop(columns=removable_constants, errors="ignore")

        if cleaned.empty:
            raise ValueError("No rows remain after corrective cleaning.")
        if cleaned.shape[1] < 2:
            raise ValueError("No usable feature columns remain after cleaning.")

        # Save a human-readable cleaned artifact. Statistical imputation, scaling,
        # and encoding are deliberately kept inside the fitted sklearn pipeline.
        self._save_dataframe(cleaned, "cleaned_dataset.csv", "cleaned_dataset")
        return self._prepare_dataframe(cleaned, corrective_cleaning_applied=True)

    def prepare_model_ready_data(self, profile: dict[str, Any]) -> dict[str, Any]:
        self.log(
            "PilotFlow",
            "CleanCraft Bypassed; building a leakage-safe model transformation pipeline",
            36,
        )
        validated = self.df[self.df[self.target].notna()].copy()
        return self._prepare_dataframe(validated, corrective_cleaning_applied=False)

    def _prepare_dataframe(
        self,
        frame: pd.DataFrame,
        corrective_cleaning_applied: bool,
    ) -> dict[str, Any]:
        X = frame.drop(columns=[self.target])
        y = frame[self.target].copy()

        numeric = list(X.select_dtypes(include=np.number).columns)
        categorical = [column for column in X.columns if column not in numeric]

        if not numeric and not categorical:
            raise ValueError("No usable feature columns were found.")

        transformer = self._build_transformer(numeric, categorical)
        target_encoder: LabelEncoder | None = None

        if self.run.problem_type == "classification" and not pd.api.types.is_numeric_dtype(y):
            target_encoder = LabelEncoder()
            y = pd.Series(
                target_encoder.fit_transform(y.astype(str)),
                index=y.index,
                name=y.name,
            )

        schema = [
            {"name": column, "type": "number" if column in numeric else "text"}
            for column in X.columns
        ]

        return {
            "X": X,
            "y": y,
            "transformer": transformer,
            "target_encoder": target_encoder,
            "schema": schema,
            "numeric": numeric,
            "categorical": categorical,
            "rows_after_cleaning": int(len(frame)),
            "corrective_cleaning_applied": corrective_cleaning_applied,
        }

    @staticmethod
    def _build_transformer(
        numeric: list[str],
        categorical: list[str],
    ) -> ColumnTransformer:
        transformers: list[tuple[str, Pipeline, list[str]]] = []

        if numeric:
            numeric_steps = Pipeline(
                [
                    ("imputer", SimpleImputer(strategy="median")),
                    ("scaler", StandardScaler()),
                ]
            )
            transformers.append(("numeric", numeric_steps, numeric))

        if categorical:
            categorical_steps = Pipeline(
                [
                    ("imputer", SimpleImputer(strategy="most_frequent")),
                    (
                        "encoder",
                        OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                    ),
                ]
            )
            transformers.append(("categorical", categorical_steps, categorical))

        return ColumnTransformer(transformers=transformers, remainder="drop")

    # ------------------------------------------------------------------
    # ModelForge Agent
    # ------------------------------------------------------------------
    def model_forge(self, prep: dict[str, Any]) -> dict[str, Any]:
        self.log(
            "ModelForge",
            f"Tuning and comparing candidate {self.run.problem_type} algorithms",
            50,
        )

        X_train, X_test, y_train, y_test = self._safe_train_test_split(
            prep["X"], prep["y"]
        )
        cv = self._build_cross_validator(y_train)
        scoring = "f1_weighted" if self.run.problem_type == "classification" else "r2"
        candidates = self._candidate_models()
        if self.run.selected_algorithms:
            candidates = [candidate for candidate in candidates if candidate[0] in self.run.selected_algorithms]
        if not candidates:
            raise ValueError("No valid algorithms were selected for training.")

        leaderboard: list[dict[str, Any]] = []
        fitted: dict[str, Pipeline] = {}

        for candidate_index, (name, estimator, parameter_space) in enumerate(candidates):
            pipeline = Pipeline(
                [
                    ("preprocessor", prep["transformer"]),
                    ("model", estimator),
                ]
            )
            combinations = self._parameter_combination_count(parameter_space)
            n_iter = min(MAX_SEARCH_ITERATIONS, combinations)

            search = RandomizedSearchCV(
                estimator=pipeline,
                param_distributions=parameter_space,
                n_iter=max(1, n_iter),
                scoring=scoring,
                cv=cv,
                refit=True,
                random_state=RANDOM_STATE,
                n_jobs=1,
                error_score="raise",
                return_train_score=True,
            )
            search.fit(X_train, y_train)
            best_pipeline = search.best_estimator_
            train_metrics = self._evaluation_metrics(
                y_train, best_pipeline.predict(X_train)
            )
            test_metrics = self._evaluation_metrics(
                y_test, best_pipeline.predict(X_test)
            )
            generalization_gap = round(
                float(train_metrics["selection_score"] - test_metrics["selection_score"]),
                5,
            )

            leaderboard.append(
                {
                    "model": name,
                    **test_metrics,
                    **{f"train_{key}": value for key, value in train_metrics.items()},
                    **{f"test_{key}": value for key, value in test_metrics.items()},
                    "generalization_gap": generalization_gap,
                    "overfitting_warning": generalization_gap > 0.1,
                    "cv_score": round(float(search.best_score_), 5),
                    "score": test_metrics["selection_score"],
                    "best_params": {
                        key.replace("model__", ""): _json_value(value)
                        for key, value in search.best_params_.items()
                    },
                }
            )
            fitted[name] = best_pipeline
            self.log(
                "ModelForge",
                f"Finished {name} ({candidate_index + 1}/{len(candidates)})",
                50 + round((candidate_index + 1) / len(candidates) * 24),
            )

        leaderboard.sort(key=lambda item: item["score"], reverse=True)
        best_name = leaderboard[0]["model"]
        best_pipeline = fitted[best_name]

        model_dir = Path(settings.MEDIA_ROOT) / "models"
        model_dir.mkdir(parents=True, exist_ok=True)
        path = model_dir / f"{self.run.id}.joblib"
        joblib.dump(
            {
                "pipeline": best_pipeline,
                "target_encoder": prep["target_encoder"],
                "target": self.target,
                "problem_type": self.run.problem_type,
                "leaderboard": leaderboard,
            },
            path,
        )

        with path.open("rb") as handle:
            saved = TrainedModel(
                run=self.run,
                name=best_name,
                feature_schema=prep["schema"],
            )
            saved.artifact.save(path.name, File(handle), save=True)

        self.log(
            "ModelForge",
            f"Tuned {len(candidates)} algorithms and selected {best_name}",
            78,
        )
        return {
            "leaderboard": leaderboard,
            "best_name": best_name,
            "pipeline": best_pipeline,
            "X_test": X_test,
            "y_test": y_test,
            "model_id": str(saved.id),
            "selection_metric": scoring,
            "cv_folds": cv.get_n_splits(),
        }

    def _candidate_models(
        self,
    ) -> list[tuple[str, BaseEstimator, dict[str, list[Any]]]]:
        if self.run.problem_type == "classification":
            return [
                (
                    "Logistic Regression",
                    LogisticRegression(max_iter=2000, random_state=RANDOM_STATE),
                    {
                        # Smaller C means stronger L2 regularization.
                        "model__C": [0.001, 0.01, 0.1, 1.0, 10.0],
                        "model__class_weight": [None, "balanced"],
                        # lbfgs supports binary and multiclass targets. liblinear
                        # is deliberately excluded because recent sklearn versions
                        # reject it for native multiclass classification.
                        "model__solver": ["lbfgs"],
                    },
                ),
                (
                    "Random Forest",
                    RandomForestClassifier(random_state=RANDOM_STATE, n_jobs=1),
                    {
                        "model__n_estimators": [100, 200, 350],
                        "model__max_depth": [3, 5, 8, 12],
                        "model__min_samples_split": [5, 10, 20],
                        "model__min_samples_leaf": [2, 4, 8],
                        "model__max_features": ["sqrt", "log2", 0.7],
                        "model__class_weight": [None, "balanced"],
                    },
                ),
                (
                    "Gradient Boosting",
                    GradientBoostingClassifier(random_state=RANDOM_STATE),
                    {
                        "model__n_estimators": [75, 125, 200],
                        "model__learning_rate": [0.03, 0.05, 0.1, 0.2],
                        "model__max_depth": [1, 2, 3],
                        "model__subsample": [0.6, 0.75, 0.9],
                        "model__min_samples_leaf": [2, 5, 10],
                    },
                ),
            ]

        return [
            (
                "Ridge Regression",
                Ridge(),
                {"model__alpha": [0.1, 1.0, 10.0, 100.0, 1000.0]},
            ),
            (
                "Random Forest",
                RandomForestRegressor(random_state=RANDOM_STATE, n_jobs=1),
                {
                    "model__n_estimators": [100, 200, 350],
                    "model__max_depth": [3, 5, 8, 12],
                    "model__min_samples_split": [5, 10, 20],
                    "model__min_samples_leaf": [2, 4, 8],
                    "model__max_features": [1.0, "sqrt", "log2"],
                },
            ),
            (
                "Gradient Boosting",
                GradientBoostingRegressor(random_state=RANDOM_STATE),
                {
                    "model__n_estimators": [75, 125, 200],
                    "model__learning_rate": [0.03, 0.05, 0.1, 0.2],
                    "model__max_depth": [1, 2, 3],
                    "model__subsample": [0.6, 0.75, 0.9],
                    "model__min_samples_leaf": [2, 5, 10],
                    "model__loss": ["squared_error", "huber"],
                },
            ),
        ]

    def _safe_train_test_split(
        self,
        X: pd.DataFrame,
        y: pd.Series,
    ) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
        stratify = None
        if self.run.problem_type == "classification":
            counts = pd.Series(y).value_counts()
            if len(counts) > 1 and counts.min() >= 2:
                # Test set must be large enough to contain at least one item/class.
                proposed_test_rows = max(1, int(math.ceil(len(y) * TEST_SIZE)))
                if proposed_test_rows >= len(counts):
                    stratify = y

        return train_test_split(
            X,
            y,
            test_size=TEST_SIZE,
            random_state=RANDOM_STATE,
            stratify=stratify,
        )

    def _build_cross_validator(self, y_train: pd.Series):
        if self.run.problem_type == "classification":
            counts = pd.Series(y_train).value_counts()
            if len(counts) < 2:
                raise ValueError("Classification training data contains only one class.")
            n_splits = min(5, int(counts.min()))
            if n_splits < 2:
                raise ValueError("Not enough samples per class for cross-validation.")
            return StratifiedKFold(
                n_splits=n_splits,
                shuffle=True,
                random_state=RANDOM_STATE,
            )

        n_splits = min(5, max(2, len(y_train) // 10))
        return KFold(n_splits=n_splits, shuffle=True, random_state=RANDOM_STATE)

    def _evaluation_metrics(
        self,
        y_true: pd.Series,
        prediction: np.ndarray,
    ) -> dict[str, Any]:
        if self.run.problem_type == "classification":
            weighted_f1 = f1_score(
                y_true, prediction, average="weighted", zero_division=0
            )
            return {
                "accuracy": round(float(accuracy_score(y_true, prediction)), 5),
                "error_rate": round(
                    float(1.0 - accuracy_score(y_true, prediction)), 5
                ),
                "balanced_accuracy": round(
                    float(balanced_accuracy_score(y_true, prediction)), 5
                ),
                "precision_weighted": round(
                    float(
                        precision_score(
                            y_true,
                            prediction,
                            average="weighted",
                            zero_division=0,
                        )
                    ),
                    5,
                ),
                "recall_weighted": round(
                    float(
                        recall_score(
                            y_true,
                            prediction,
                            average="weighted",
                            zero_division=0,
                        )
                    ),
                    5,
                ),
                "f1_weighted": round(float(weighted_f1), 5),
                "f1_macro": round(
                    float(f1_score(y_true, prediction, average="macro", zero_division=0)),
                    5,
                ),
                "selection_score": round(float(weighted_f1), 5),
            }

        r2 = r2_score(y_true, prediction)
        return {
            "r2": round(float(r2), 5),
            "mae": round(float(mean_absolute_error(y_true, prediction)), 5),
            "rmse": round(
                float(mean_squared_error(y_true, prediction) ** 0.5), 5
            ),
            "selection_score": round(float(r2), 5),
        }

    # ------------------------------------------------------------------
    # InsightBoard Agent
    # ------------------------------------------------------------------
    def insight_board(
        self,
        profile: dict[str, Any],
        prep: dict[str, Any],
        training: dict[str, Any],
        route: dict[str, Any],
    ) -> dict[str, Any]:
        self.log(
            "InsightBoard",
            "Calculating model-agnostic explanations and preparing the report",
            88,
        )

        scoring = (
            "f1_weighted" if self.run.problem_type == "classification" else "r2"
        )
        importance = permutation_importance(
            training["pipeline"],
            training["X_test"],
            training["y_test"],
            n_repeats=8,
            random_state=RANDOM_STATE,
            scoring=scoring,
            n_jobs=1,
        )
        contributions = sorted(
            [
                {
                    "feature": name,
                    "importance": round(max(0.0, float(value)), 6),
                }
                for name, value in zip(
                    training["X_test"].columns,
                    importance.importances_mean,
                )
            ],
            key=lambda item: item["importance"],
            reverse=True,
        )

        explanation_method = "permutation importance (model-agnostic global XAI)"
        local_surrogate: list[dict[str, Any]] = []
        try:
            local_surrogate = self._local_surrogate_contributions(prep, training)
        except Exception as exc:  # XAI fallback must not fail the workflow.
            self.log(
                "InsightBoard",
                f"Local surrogate explanation skipped: {exc}",
                92,
            )

        route_text = (
            "routed the data through CleanCraft"
            if route["needs_corrective_cleaning"]
            else "bypassed corrective cleaning and proceeded to ModelForge"
        )
        summary = (
            f"PilotFlow identified a {profile['problem_type']} problem, {route_text}. "
            f"ModelForge selected {training['best_name']} after tuned cross-validation."
        )

        report = {
            "summary": summary,
            "dataset": profile,
            "routing": route,
            "preprocessing": {
                "applied": prep["corrective_cleaning_applied"],
                "corrective_cleaning_applied": prep[
                    "corrective_cleaning_applied"
                ],
                "model_pipeline_transformations_applied": True,
                "numeric_columns": prep["numeric"],
                "categorical_columns": prep["categorical"],
                "rows_after_cleaning": prep["rows_after_cleaning"],
            },
            "training": {
                "leaderboard": training["leaderboard"],
                "best_model": training["best_name"],
                "model_id": training["model_id"],
                "selection_metric": training["selection_metric"],
                "cv_folds": training["cv_folds"],
            },
            "explainability": {
                "global_method": explanation_method,
                "global_feature_contributions": contributions,
                "local_method": (
                    "local linear surrogate inspired by LIME"
                    if local_surrogate
                    else None
                ),
                "local_feature_contributions": local_surrogate,
            },
            "target_column": self.target,
            "configuration": {
                "mode": self.run.mode,
                "target_column": self.target,
                "target_selection_reason": self.run.target_selection_reason,
                "selected_algorithms": self.run.selected_algorithms,
            },
        }
        # Backward-compatible fields consumed by the existing API and UI.
        report.update({
            "leaderboard": training["leaderboard"],
            "best_model": training["best_name"],
            "model_id": training["model_id"],
            "explanation_method": "LIME" if local_surrogate else explanation_method,
            "feature_contributions": contributions,
        })
        self._save_report(report)
        self.log(
            "InsightBoard",
            "Metrics, explanations, and downloadable artifacts are ready",
            100,
        )
        return report

    def _local_surrogate_contributions(
        self,
        prep: dict[str, Any],
        training: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """Approximate local explanations; accurately labelled as LIME-inspired."""
        transformer = training["pipeline"].named_steps["preprocessor"]
        estimator = training["pipeline"].named_steps["model"]
        transformed = np.asarray(
            transformer.transform(training["X_test"]), dtype=float
        )
        if transformed.size == 0:
            return []

        names = list(transformer.get_feature_names_out())
        rng = np.random.default_rng(RANDOM_STATE)
        scale = np.std(transformed, axis=0)
        scale[scale == 0] = 1.0
        totals = np.zeros(transformed.shape[1], dtype=float)
        count = min(5, len(transformed))

        for row in transformed[:count]:
            samples = row + rng.normal(size=(400, len(row))) * scale * 0.35
            distances = np.linalg.norm((samples - row) / scale, axis=1)
            weights = np.exp(-(distances**2) / max(1.0, len(row) * 0.75))

            if self.run.problem_type == "classification":
                if not hasattr(estimator, "predict_proba"):
                    continue
                probabilities = estimator.predict_proba(samples)
                predicted_class = estimator.predict(row.reshape(1, -1))[0]
                class_index = list(estimator.classes_).index(predicted_class)
                outcomes = probabilities[:, class_index]
            else:
                outcomes = estimator.predict(samples)

            surrogate = Ridge(alpha=1.0)
            surrogate.fit(samples, outcomes, sample_weight=weights)
            totals += np.abs(surrogate.coef_ * scale)

        grouped: dict[str, float] = {}
        for transformed_name, value in zip(names, totals / max(1, count)):
            clean_name = transformed_name.split("__", 1)[-1]
            original = next(
                (
                    column["name"]
                    for column in prep["schema"]
                    if clean_name == column["name"]
                    or clean_name.startswith(f"{column['name']}_")
                ),
                clean_name,
            )
            grouped[original] = grouped.get(original, 0.0) + float(value)

        return [
            {"feature": feature, "importance": round(value, 6)}
            for feature, value in sorted(
                grouped.items(), key=lambda item: item[1], reverse=True
            )
        ]

    # ------------------------------------------------------------------
    # Profiling helpers
    # ------------------------------------------------------------------
    def _infer_problem_type(self, target: pd.Series) -> dict[str, Any]:
        return infer_problem_type(target)

    @staticmethod
    def _correlation_matrix(features: pd.DataFrame) -> dict[str, Any]:
        numeric = features.select_dtypes(include=np.number).replace([np.inf, -np.inf], np.nan)
        columns = list(numeric.columns[:20])
        if not columns:
            return {"columns": [], "values": []}
        correlation = numeric[columns].corr().fillna(0)
        return {"columns": columns, "values": [[round(float(value), 4) for value in row] for row in correlation.to_numpy()]}

    @staticmethod
    def _identifier_like_columns(features: pd.DataFrame) -> list[str]:
        identifiers: list[str] = []
        rows = max(1, len(features))
        for column in features.columns:
            lower = column.lower().strip()
            uniqueness = features[column].nunique(dropna=True) / rows
            name_signal = lower == "id" or lower.endswith("_id") or "uuid" in lower
            if name_signal or uniqueness >= 0.98:
                identifiers.append(column)
        return identifiers

    @staticmethod
    def _detect_scaling_need(numeric: pd.DataFrame) -> dict[str, Any]:
        if numeric.empty:
            return {"needs_scaling": False, "scale_ratio": None}

        ranges = (numeric.max(skipna=True) - numeric.min(skipna=True)).replace(
            [np.inf, -np.inf], np.nan
        )
        positive = ranges[(ranges > 0) & ranges.notna()]
        if positive.empty:
            return {"needs_scaling": False, "scale_ratio": None}

        ratio = float(positive.max() / positive.min())
        return {
            "needs_scaling": bool(ratio > 100),
            "scale_ratio": round(ratio, 4),
        }

    @staticmethod
    def _detect_outliers(numeric: pd.DataFrame) -> dict[str, Any]:
        counts: dict[str, int] = {}
        for column in numeric.columns:
            series = pd.to_numeric(numeric[column], errors="coerce").dropna()
            if len(series) < 4:
                continue
            q1 = series.quantile(0.25)
            q3 = series.quantile(0.75)
            iqr = q3 - q1
            if iqr <= 0:
                continue
            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr
            count = int(((series < lower) | (series > upper)).sum())
            if count:
                counts[column] = count
        return {
            "columns_with_outliers": list(counts),
            "outlier_counts": counts,
            "method": "IQR diagnostic only; rows are not automatically removed",
        }

    @staticmethod
    def _basic_statistics(features: pd.DataFrame) -> dict[str, Any]:
        statistics: dict[str, Any] = {}
        numeric = features.select_dtypes(include=np.number)
        for column in numeric.columns:
            series = pd.to_numeric(numeric[column], errors="coerce")
            statistics[column] = {
                "mean": _finite_or_none(series.mean()),
                "median": _finite_or_none(series.median()),
                "std": _finite_or_none(series.std()),
                "min": _finite_or_none(series.min()),
                "max": _finite_or_none(series.max()),
                "skewness": _finite_or_none(series.skew()),
            }
        return statistics

    @staticmethod
    def _parameter_combination_count(parameter_space: dict[str, list[Any]]) -> int:
        total = 1
        for values in parameter_space.values():
            total *= max(1, len(values))
        return total

    # ------------------------------------------------------------------
    # Persistence helpers
    # ------------------------------------------------------------------
    def _handle_failure(self, exc: Exception) -> None:
        self.run.status = "failed"
        self.run.error = str(exc)
        logs = list(self.run.logs or [])
        logs.append(
            {
                "time": datetime.now(timezone.utc).isoformat(),
                "agent": self.run.current_agent or "PilotFlow",
                "message": f"Workflow stopped: {exc}",
            }
        )
        self.run.logs = logs
        self.run.save()

    def _save_dataframe(self, frame: pd.DataFrame, name: str, kind: str) -> None:
        folder = Path(settings.MEDIA_ROOT) / "artifacts" / str(self.run.id)
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / name
        frame.to_csv(path, index=False)
        with path.open("rb") as handle:
            artifact = Artifact(run=self.run, kind=kind, name=name)
            artifact.file.save(f"{self.run.id}/{name}", File(handle), save=True)

    def _save_report(self, report: dict[str, Any]) -> None:
        folder = Path(settings.MEDIA_ROOT) / "artifacts" / str(self.run.id)
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / "report.json"
        path.write_text(json.dumps(report, indent=2, default=_json_value), encoding="utf-8")
        with path.open("rb") as handle:
            artifact = Artifact(run=self.run, kind="report", name="report.json")
            artifact.file.save(
                f"{self.run.id}/report.json",
                File(handle),
                save=True,
            )
