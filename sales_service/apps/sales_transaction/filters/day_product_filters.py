import django_filters
from apps.sales_transaction.models.aggregate_quotation import AggregateQuotationMain
from apps.sales_transaction.models.scrap_quotation import ScrapQuotationMain
from apps.sales_transaction.models.noc_document import NocDocument
from apps.sales_transaction.models.daily_target_disposal import DailyTargetDisposalMain
from apps.sales_transaction.models.afr_transport_rfq import AfrTransportRfq
from apps.sales_transaction.models.aggregate_entry import AggregateEntryMain
from apps.sales_transaction.models.afr_transport_entry import AfrTransportEntryMain


class AggregateQuotationFilter(django_filters.FilterSet):
    quote_month = django_filters.CharFilter(lookup_expr="iexact")
    site_id = django_filters.UUIDFilter()
    party_name = django_filters.CharFilter(lookup_expr="icontains")
    created_at_after = django_filters.DateFilter(field_name="created_at", lookup_expr="gte")
    created_at_before = django_filters.DateFilter(field_name="created_at", lookup_expr="lte")

    class Meta:
        model = AggregateQuotationMain
        fields = ["quote_month", "site_id", "party_name"]


class ScrapQuotationFilter(django_filters.FilterSet):
    quote_month = django_filters.CharFilter(lookup_expr="iexact")
    site_id = django_filters.UUIDFilter()
    party_name = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = ScrapQuotationMain
        fields = ["quote_month", "site_id", "party_name"]


class NocDocumentFilter(django_filters.FilterSet):
    scrap_customer_id = django_filters.UUIDFilter()
    site_id = django_filters.UUIDFilter()
    approve_status = django_filters.CharFilter()
    overall_approve_status = django_filters.CharFilter()

    class Meta:
        model = NocDocument
        fields = ["scrap_customer_id", "site_id", "approve_status", "overall_approve_status"]


class DailyTargetDisposalFilter(django_filters.FilterSet):
    site_id = django_filters.UUIDFilter()
    entry_date_after = django_filters.DateFilter(field_name="entry_date", lookup_expr="gte")
    entry_date_before = django_filters.DateFilter(field_name="entry_date", lookup_expr="lte")

    class Meta:
        model = DailyTargetDisposalMain
        fields = ["site_id", "entry_date"]


class AfrTransportRfqFilter(django_filters.FilterSet):
    request_quotation_transportation = django_filters.CharFilter(lookup_expr="iexact")
    due_date_after = django_filters.DateFilter(field_name="due_date", lookup_expr="gte")
    due_date_before = django_filters.DateFilter(field_name="due_date", lookup_expr="lte")
    site_id = django_filters.UUIDFilter()

    class Meta:
        model = AfrTransportRfq
        fields = ["request_quotation_transportation", "site_id"]


class AggregateEntryFilter(django_filters.FilterSet):
    site_id = django_filters.UUIDFilter()
    scrap_no = django_filters.CharFilter(lookup_expr="icontains")
    entry_date_after = django_filters.DateFilter(field_name="entry_date", lookup_expr="gte")
    entry_date_before = django_filters.DateFilter(field_name="entry_date", lookup_expr="lte")

    class Meta:
        model = AggregateEntryMain
        fields = ["site_id", "scrap_no", "entry_date"]


class AfrTransportEntryFilter(django_filters.FilterSet):
    site_id = django_filters.UUIDFilter()
    trans_appr_no = django_filters.CharFilter(lookup_expr="icontains")
    approval_status = django_filters.CharFilter()
    entry_date_after = django_filters.DateFilter(field_name="entry_date", lookup_expr="gte")
    entry_date_before = django_filters.DateFilter(field_name="entry_date", lookup_expr="lte")

    class Meta:
        model = AfrTransportEntryMain
        fields = ["site_id", "trans_appr_no", "approval_status", "entry_date"]
