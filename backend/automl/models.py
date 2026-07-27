import uuid
from django.db import models


class Dataset(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to="datasets/")
    rows = models.PositiveIntegerField()
    columns = models.PositiveIntegerField()
    column_names = models.JSONField(default=list)
    preview = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)


class Run(models.Model):
    STATUS_CHOICES = [("pending", "Pending"), ("running", "Running"), ("completed", "Completed"), ("failed", "Failed")]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name="runs")
    mode = models.CharField(max_length=16, default="auto")
    target_column = models.CharField(max_length=255)
    target_selection_reason = models.TextField(blank=True)
    selected_algorithms = models.JSONField(default=list)
    problem_type = models.CharField(max_length=32, blank=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="pending")
    progress = models.PositiveSmallIntegerField(default=0)
    current_agent = models.CharField(max_length=64, default="PilotFlow")
    logs = models.JSONField(default=list)
    results = models.JSONField(default=dict)
    error = models.TextField(blank=True)
    checkpoint_stage = models.CharField(max_length=64, blank=True)
    workflow_state = models.JSONField(default=dict)
    recovery_attempts = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class TrainedModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    run = models.OneToOneField(Run, on_delete=models.CASCADE, related_name="trained_model")
    name = models.CharField(max_length=100)
    artifact = models.FileField(upload_to="models/")
    feature_schema = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)


class Artifact(models.Model):
    run = models.ForeignKey(Run, on_delete=models.CASCADE, related_name="artifacts")
    kind = models.CharField(max_length=32)
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to="artifacts/")
    created_at = models.DateTimeField(auto_now_add=True)
