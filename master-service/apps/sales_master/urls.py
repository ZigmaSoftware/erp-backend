from rest_framework.routers import DefaultRouter

from apps.sales_master.views.scrap_sales_category_master_viewset import (
    ScrapSalesCategoryMasterViewSet,
)
from apps.sales_master.views.item_type_master_viewset import (
    ItemTypeMasterViewSet,
)
from apps.sales_master.views.item_creation_viewset import (
    ItemCreationViewSet,
)

router = DefaultRouter()

router.register(
    r"scrap-sales-categories",
    ScrapSalesCategoryMasterViewSet,
    basename="scrap-sales-category",
)
router.register(
    r"item-types",
    ItemTypeMasterViewSet,
    basename="item-type",
)
router.register(
    r"item-creations",
    ItemCreationViewSet,
    basename="item-creation",
)

urlpatterns = router.urls
