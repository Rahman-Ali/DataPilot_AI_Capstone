import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(name="Dataset", fields=[
            ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
            ("name", models.CharField(max_length=255)),
            ("file", models.FileField(upload_to="datasets/")),
            ("rows", models.PositiveIntegerField()),
            ("columns", models.PositiveIntegerField()),
            ("column_names", models.JSONField(default=list)),
            ("preview", models.JSONField(default=list)),
            ("created_at", models.DateTimeField(auto_now_add=True)),
        ]),
        migrations.CreateModel(name="Run", fields=[
            ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
            ("mode", models.CharField(default="auto", max_length=16)),
            ("target_column", models.CharField(max_length=255)),
            ("problem_type", models.CharField(blank=True, max_length=32)),
            ("status", models.CharField(choices=[("pending", "Pending"), ("running", "Running"), ("completed", "Completed"), ("failed", "Failed")], default="pending", max_length=16)),
            ("progress", models.PositiveSmallIntegerField(default=0)),
            ("current_agent", models.CharField(default="PilotFlow", max_length=64)),
            ("logs", models.JSONField(default=list)),
            ("results", models.JSONField(default=dict)),
            ("error", models.TextField(blank=True)),
            ("created_at", models.DateTimeField(auto_now_add=True)),
            ("updated_at", models.DateTimeField(auto_now=True)),
            ("dataset", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="runs", to="automl.dataset")),
        ]),
        migrations.CreateModel(name="TrainedModel", fields=[
            ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
            ("name", models.CharField(max_length=100)),
            ("artifact", models.FileField(upload_to="models/")),
            ("feature_schema", models.JSONField(default=list)),
            ("created_at", models.DateTimeField(auto_now_add=True)),
            ("run", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="trained_model", to="automl.run")),
        ]),
        migrations.CreateModel(name="Artifact", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("kind", models.CharField(max_length=32)),
            ("name", models.CharField(max_length=255)),
            ("file", models.FileField(upload_to="artifacts/")),
            ("created_at", models.DateTimeField(auto_now_add=True)),
            ("run", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="artifacts", to="automl.run")),
        ]),
    ]
