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
from apps.sales_master.views.terms_of_payment_creation_master_viewset import (
    TermsOfPaymentCreationMasterViewSet,
)
from apps.sales_master.views.mail_details_creation_master_viewset import (
    MailDetailsCreationMasterViewSet,
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
    r"terms-of-payment-creations",
    TermsOfPaymentCreationMasterViewSet,
    basename="terms-of-payment-creation",
)
router.register(
    r"mail-details-creations",
    MailDetailsCreationMasterViewSet,
    basename="mail-details-creation",
)

urlpatterns = router.urls
