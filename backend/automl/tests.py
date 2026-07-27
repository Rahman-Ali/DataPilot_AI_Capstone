import io
import time
from pathlib import Path

import pandas as pd
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from rest_framework.test import APITransactionTestCase


@override_settings(MEDIA_ROOT=Path(__file__).resolve().parent.parent / "test-runtime")
class WorkflowApiTests(APITransactionTestCase):
    def upload(self, frame, name="sample.csv"):
        stream = io.StringIO()
        frame.to_csv(stream, index=False)
        response = self.client.post(
            "/api/datasets/upload/",
            {"file": SimpleUploadedFile(name, stream.getvalue().encode(), content_type="text/csv")},
            format="multipart",
        )
        self.assertEqual(response.status_code, 201, response.data)
        return response.data

    def wait_for_run(self, run_id, timeout=120):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            response = self.client.get(f"/api/runs/{run_id}/status/")
            if response.data["status"] in {"completed", "failed"}:
                self.assertEqual(response.data["status"], "completed", response.data)
                return response.data
            time.sleep(0.1)
        self.fail("The background workflow did not finish before the test timeout.")

    def test_dirty_classification_workflow_and_prediction(self):
        frame = pd.DataFrame({
            "age": [20 + index % 35 for index in range(80)],
            "city": ["Lahore", "Karachi", None, "Islamabad"] * 20,
            "spend": [None if index % 11 == 0 else 100 + index * 2 for index in range(80)],
            "churn": ["yes" if index % 3 == 0 else "no" for index in range(80)],
        })
        dataset = self.upload(frame)
        start = self.client.post("/api/runs/start/", {"dataset_id": dataset["id"], "mode": "auto"}, format="json")
        self.assertEqual(start.status_code, 202, start.data)
        self.assertEqual(start.data["target_column"], "churn")
        self.assertTrue(start.data["target_selection_reason"])
        self.wait_for_run(start.data["run_id"])
        results = self.client.get(f"/api/runs/{start.data['run_id']}/results/")
        self.assertEqual(results.status_code, 200)
        self.assertTrue(results.data["routing"]["needs_cleaning"])
        self.assertEqual(len(results.data["leaderboard"]), 3)
        first_model = results.data["leaderboard"][0]
        for metric in ("train_accuracy", "test_accuracy", "train_error_rate", "test_error_rate", "generalization_gap"):
            self.assertIn(metric, first_model)
        self.assertIn("data_quality", results.data["dataset"])
        self.assertIn("correlation_matrix", results.data["dataset"])
        self.assertEqual(results.data["explanation_method"], "LIME")
        prediction = self.client.post(f"/api/models/{results.data['model_id']}/predict/", {
            "features": {"age": 32, "city": "Lahore", "spend": 240},
        }, format="json")
        self.assertEqual(prediction.status_code, 200, prediction.data)
        self.assertIn(prediction.data["prediction"], ["yes", "no"])

    def test_clean_numeric_data_bypasses_cleancraft(self):
        frame = pd.DataFrame({
            "x1": range(60),
            "x2": [index * 2.5 for index in range(60)],
            "target": [index * 1.7 + 3 for index in range(60)],
        })
        dataset = self.upload(frame, "clean.csv")
        start = self.client.post("/api/runs/start/", {
            "dataset_id": dataset["id"], "target_column": "target", "mode": "guided",
            "algorithms": ["Ridge Regression"],
        }, format="json")
        self.assertEqual(start.status_code, 202, start.data)
        self.wait_for_run(start.data["run_id"])
        results = self.client.get(f"/api/runs/{start.data['run_id']}/results/")
        self.assertFalse(results.data["routing"]["needs_cleaning"])
        self.assertEqual([row["model"] for row in results.data["leaderboard"]], ["Ridge Regression"])
        ridge = results.data["leaderboard"][0]
        for metric in ("train_r2", "test_r2", "train_mae", "test_mae", "train_rmse", "test_rmse"):
            self.assertIn(metric, ridge)
        messages = [entry["message"] for entry in self.client.get(f"/api/runs/{start.data['run_id']}/status/").data["logs"]]
        self.assertTrue(any("Bypassed" in message for message in messages))

    def test_multiclass_logistic_regression_completes(self):
        frame = pd.DataFrame({
            "duration": [20 + index % 30 for index in range(100)],
            "events": [index % 12 for index in range(100)],
            "user_behavior_class": [f"class_{index % 5}" for index in range(100)],
        })
        dataset = self.upload(frame, "multiclass.csv")
        start = self.client.post("/api/runs/start/", {
            "dataset_id": dataset["id"],
            "target_column": "user_behavior_class",
            "mode": "guided",
            "algorithms": ["Logistic Regression"],
        }, format="json")
        self.assertEqual(start.status_code, 202, start.data)
        status_response = self.wait_for_run(start.data["run_id"])
        self.assertEqual(status_response["progress"], 100)
        results = self.client.get(f"/api/runs/{start.data['run_id']}/results/")
        self.assertEqual(results.status_code, 200, results.data)
        self.assertEqual(results.data["leaderboard"][0]["model"], "Logistic Regression")
