from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("automl", "0002_run_configuration"),
    ]

    operations = [
        migrations.AddField(
            model_name="run",
            name="checkpoint_stage",
            field=models.CharField(blank=True, max_length=64),
        ),
        migrations.AddField(
            model_name="run",
            name="workflow_state",
            field=models.JSONField(default=dict),
        ),
        migrations.AddField(
            model_name="run",
            name="recovery_attempts",
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]
