from django.urls import path
from . import views

urlpatterns = [
    path("health/", views.health),
    path("dashboard/", views.dashboard),
    path("datasets/upload/", views.upload_dataset),
    path("runs/start/", views.start_run),
    path("runs/<uuid:run_id>/status/", views.run_status),
    path("runs/<uuid:run_id>/results/", views.run_results),
    path("runs/<uuid:run_id>/artifacts/", views.run_artifacts),
    path("models/<uuid:model_id>/predict/", views.predict),
]
