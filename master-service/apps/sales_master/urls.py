from rest_framework.routers import DefaultRouter

from apps.sales_master.views.scrap_sales_category_master_viewset import (
    ScrapSalesCategoryMasterViewSet,
)
from apps.sales_master.views.item_type_master_viewset import (
    ItemTypeMasterViewSet,
)
from apps.sales_master.views.item_group_creation_master_viewset import (
    ItemGroupCreationMasterViewSet,
)
from apps.sales_master.views.transport_medium_creation_master_viewset import (
    TransportMediumCreationMasterViewSet,
)
from apps.sales_master.views.terms_of_delivery_creation_master_viewset import (
    TermsOfDeliveryCreationMasterViewSet,
)
from apps.sales_master.views.terms_of_payment_creation_master_viewset import (
    TermsOfPaymentCreationMasterViewSet,
)
from apps.sales_master.views.mail_details_creation_master_viewset import (
    MailDetailsCreationMasterViewSet,
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
from apps.sales_master.views.sub_category_master_viewset import (
    SubCategoryMasterViewSet,
)
from apps.sales_master.views.target_entry_master_viewset import (
    TargetEntryMasterViewSet,
)
from apps.sales_master.views.target_entry_item_viewset import (
    TargetEntryItemViewSet,
)
from apps.sales_master.views.rdf_inerts_perc_entry_viewset import (
    RdfInertsPercEntryViewSet,
)
from apps.sales_master.views.icw_supplier_creation_viewset import (
    IcwSupplierCreationViewSet,
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
    r"item-group-creations",
    ItemGroupCreationMasterViewSet,
    basename="item-group-creation",
)
router.register(
    r"transport-medium-creations",
    TransportMediumCreationMasterViewSet,
    basename="transport-medium-creation",
)
router.register(
    r"terms-of-delivery-creations",
    TermsOfDeliveryCreationMasterViewSet,
    basename="terms-of-delivery-creation",
)
router.register(
    r"terms-of-payment-creations",
    TermsOfPaymentCreationMasterViewSet,
    basename="terms-of-payment-creation",
)
router.register(
    r"mail-details-creations",
    MailDetailsCreationMasterViewSet,
    basename="mail-details-creation",
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
router.register(
    r"sub-categories",
    SubCategoryMasterViewSet,
    basename="sub-category",
)
router.register(
    r"target-entries",
    TargetEntryMasterViewSet,
    basename="target-entry",
)
router.register(
    r"target-entry-items",
    TargetEntryItemViewSet,
    basename="target-entry-item",
)
router.register(
    r"rdf-inerts-perc-entries",
    RdfInertsPercEntryViewSet,
    basename="rdf-inerts-perc-entry",
)
router.register(
    r"icw-supplier-creations",
    IcwSupplierCreationViewSet,
    basename="icw-supplier-creation",
)

urlpatterns = router.urls
