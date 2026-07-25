from rest_framework.routers import DefaultRouter

from apps.stores_master.views.unit_creation_master_viewset import (
    UnitCreationMasterViewSet,
)
from apps.stores_master.views.group_creation_master_viewset import (
    GroupCreationMasterViewSet,
)
from apps.stores_master.views.subgroup_creation_master_viewset import (
    SubGroupCreationMasterViewSet,
)
from apps.stores_master.views.item_min_max_type_master_viewset import (
    ItemMinMaxTypeMasterViewSet,
)
from apps.stores_master.views.item_min_max_level_master_viewset import (
    ItemMinMaxLevelMasterViewSet,
)
from apps.stores_master.views.main_task_creation_master_viewset import (
    MainTaskCreationMasterViewSet,
)
from apps.stores_master.views.task_creation_master_viewset import (
    TaskCreationMasterViewSet,
)
from apps.stores_master.views.godown_creation_master_viewset import (
    GodownCreationMasterViewSet,
)
from apps.stores_master.views.supplier_creation_master_viewset import (
    SupplierCreationMasterViewSet,
)
from apps.stores_master.views.supplier_supporting_document_viewset import (
    SupplierSupportingDocumentViewSet,
)
from apps.stores_master.views.remark_site_store_creation_master_viewset import (
    RemarkSiteStoreCreationMasterViewSet,
)

router = DefaultRouter()

router.register(
    r"unit-creations",
    UnitCreationMasterViewSet,
    basename="unit-creation",
)
router.register(
    r"group-creations",
    GroupCreationMasterViewSet,
    basename="group-creation",
)
router.register(
    r"subgroup-creations",
    SubGroupCreationMasterViewSet,
    basename="subgroup-creation",
)
router.register(
    r"item-min-max-types",
    ItemMinMaxTypeMasterViewSet,
    basename="item-min-max-type",
)
router.register(
    r"item-min-max-levels",
    ItemMinMaxLevelMasterViewSet,
    basename="item-min-max-level",
)
router.register(
    r"main-task-creations",
    MainTaskCreationMasterViewSet,
    basename="main-task-creation",
)
router.register(
    r"task-creations",
    TaskCreationMasterViewSet,
    basename="task-creation",
)
router.register(
    r"godown-creations",
    GodownCreationMasterViewSet,
    basename="godown-creation",
)
router.register(
    r"supplier-creations",
    SupplierCreationMasterViewSet,
    basename="supplier-creation",
)
router.register(
    r"supplier-supporting-documents",
    SupplierSupportingDocumentViewSet,
    basename="supplier-supporting-document",
)
router.register(
    r"remark-site-store-creations",
    RemarkSiteStoreCreationMasterViewSet,
    basename="remark-site-store-creation",
)

urlpatterns = router.urls
