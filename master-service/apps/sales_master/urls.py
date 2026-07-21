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
from apps.sales_master.views.document_type_master_viewset import (
    DocumentTypeMasterViewSet,
)
from apps.sales_master.views.transport_entry_master_viewset import (
    TransportEntryMasterViewSet,
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
router.register(
    r"document-types",
    DocumentTypeMasterViewSet,
    basename="document-type",
)
router.register(
    r"transport-entries",
    TransportEntryMasterViewSet,
    basename="transport-entry",
)

urlpatterns = router.urls
