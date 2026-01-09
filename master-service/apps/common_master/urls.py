from rest_framework.routers import DefaultRouter
from django.urls import path
from apps.common_master.views.city import CityViewSet
from apps.common_master.views.continent import ContinentViewSet
from apps.common_master.views.country import CountryViewSet
from apps.common_master.views.district import DistrictViewSet
from apps.common_master.views.plant import PlantViewSet
from apps.common_master.views.site import SiteViewSet
from apps.common_master.views.state import StateViewSet
from apps.common_master.views.debug import DebugHeadersView

router = DefaultRouter()
router.register(r"continents", ContinentViewSet, basename="continent")
router.register(r"countries", CountryViewSet, basename="country")
router.register(r"states", StateViewSet, basename="state")
router.register(r"districts", DistrictViewSet, basename="district")
router.register(r"cities", CityViewSet, basename="city")
router.register(r"sites", SiteViewSet, basename="site")
router.register(r"plants", PlantViewSet, basename="plant")

urlpatterns = router.urls + [
    path("debug/headers/", DebugHeadersView.as_view(), name="debug-headers"),
]
