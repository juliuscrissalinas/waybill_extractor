from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ExtractionModelViewSet, WaybillImageViewSet, test_api

router = DefaultRouter()
router.register(r"extraction-models", ExtractionModelViewSet)
router.register(r"waybills", WaybillImageViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("test-api/", test_api, name="test-api"),
]
