from django.conf import settings
from django.contrib import admin
from django.http import HttpResponse, JsonResponse
from django.urls import include, path, re_path
from django.views.static import serve


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
]

if settings.SERVE_MEDIA:
    urlpatterns += [
        re_path(
            r"^media/(?P<path>.*)$",
            serve,
            {"document_root": settings.MEDIA_ROOT},
        )
    ]
