import django_filters
from apps.sales_transaction.models.icw_work_order import IcwWorkOrder
from apps.sales_transaction.models.negative_invoice import NegativeInvoice
from apps.sales_transaction.models.freight_letter import FreightLetter
from apps.sales_transaction.models.co_processing import CoProcessingCertificate
from apps.sales_transaction.models.aggregate_comparison import AggregateComparison
from apps.sales_transaction.models.scrap_quotation_comparison import ScrapQuotationComparison
from apps.sales_transaction.models.confirmation_receipt import ConfirmationReceiptDc


class IcwWorkOrderFilter(django_filters.FilterSet):
    entry_date_after = django_filters.DateFilter(field_name="entry_date", lookup_expr="gte")
    entry_date_before = django_filters.DateFilter(field_name="entry_date", lookup_expr="lte")
    site_id = django_filters.UUIDFilter()
    customer_name = django_filters.UUIDFilter()
    invoice_no = django_filters.CharFilter(lookup_expr="icontains")
    approve_status = django_filters.CharFilter()

    class Meta:
        model = IcwWorkOrder
        fields = []


class NegativeInvoiceFilter(django_filters.FilterSet):
    entry_date_after = django_filters.DateFilter(field_name="entry_date", lookup_expr="gte")
    entry_date_before = django_filters.DateFilter(field_name="entry_date", lookup_expr="lte")
    site_id = django_filters.UUIDFilter()
    customer_name = django_filters.UUIDFilter()
    invoice_no = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = NegativeInvoice
        fields = []


class FreightLetterFilter(django_filters.FilterSet):
    entry_date_after = django_filters.DateFilter(field_name="entry_date", lookup_expr="gte")
    entry_date_before = django_filters.DateFilter(field_name="entry_date", lookup_expr="lte")
    site_id = django_filters.UUIDFilter()
    customer_name = django_filters.UUIDFilter()

    class Meta:
        model = FreightLetter
        fields = []


class CoProcessingFilter(django_filters.FilterSet):
    entry_date_after = django_filters.DateFilter(field_name="entry_date", lookup_expr="gte")
    entry_date_before = django_filters.DateFilter(field_name="entry_date", lookup_expr="lte")
    site_id = django_filters.UUIDFilter()
    customer_name = django_filters.UUIDFilter()
    cpc_month = django_filters.CharFilter(lookup_expr="iexact")

    class Meta:
        model = CoProcessingCertificate
        fields = []


class AggregateComparisonFilter(django_filters.FilterSet):
    quote_month = django_filters.CharFilter(lookup_expr="iexact")
    site_id = django_filters.UUIDFilter()
    status = django_filters.CharFilter()

    class Meta:
        model = AggregateComparison
        fields = []


class ScrapQuotationComparisonFilter(django_filters.FilterSet):
    quote_month = django_filters.CharFilter(lookup_expr="iexact")
    site_id = django_filters.UUIDFilter()
    status = django_filters.CharFilter()

    class Meta:
        model = ScrapQuotationComparison
        fields = []


class ConfirmationReceiptFilter(django_filters.FilterSet):
    site_id = django_filters.UUIDFilter()
    scrap_customer_id = django_filters.UUIDFilter()
    approve_status = django_filters.CharFilter()
    month_year = django_filters.CharFilter(lookup_expr="iexact")

    class Meta:
        model = ConfirmationReceiptDc
        fields = []
