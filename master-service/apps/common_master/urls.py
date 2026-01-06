from rest_framework.routers import DefaultRouter
from django.urls import path
from apps.common_master.views.site import SiteViewSet
from apps.common_master.views.plant import PlantViewSet
from apps.common_master.views.debug import DebugHeadersView

router = DefaultRouter()
router.register(r"sites", SiteViewSet, basename="site")
router.register(r"plants", PlantViewSet, basename="plant")

urlpatterns = router.urls + [
    path("debug/headers/", DebugHeadersView.as_view(), name="debug-headers"),
]

