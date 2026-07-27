from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import HttpResponse, JsonResponse
from django.urls import include, path


def service_root(request):
    return JsonResponse({
        "service": "DataPilot AI backend",
        "status": "ok",
        "api": "/api/",
        "health": "/api/health/",
        "frontend": "http://localhost:5173/",
    })


def favicon(request):
    return HttpResponse(status=204)


urlpatterns = [
    path("", service_root),
    path("favicon.ico", favicon),
    path("admin/", admin.site.urls),
    path("api/", include("automl.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
