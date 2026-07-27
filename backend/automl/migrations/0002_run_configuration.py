from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("automl", "0001_initial")]
    operations = [
        migrations.AddField(model_name="run", name="target_selection_reason", field=models.TextField(blank=True)),
        migrations.AddField(model_name="run", name="selected_algorithms", field=models.JSONField(default=list)),
    ]
