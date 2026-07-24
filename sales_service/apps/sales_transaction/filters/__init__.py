import django_filters

from apps.sales_transaction.models.work_order import WorkOrderMain
from apps.sales_transaction.models.sales_order import SalesOrderStatus
from apps.sales_transaction.models.freight_creation import FreightCreation
from apps.sales_transaction.models.dc_entry import DcEntryForm
from apps.sales_transaction.models.invoice_generation import InvoiceGeneration
from apps.sales_transaction.models.payable_entry import PayableEntryMain


class WorkOrderFilter(django_filters.FilterSet):
    entry_date_after = django_filters.DateFilter(field_name="entry_date", lookup_expr="gte")
    entry_date_before = django_filters.DateFilter(field_name="entry_date", lookup_expr="lte")
    site_id = django_filters.UUIDFilter(field_name="site_id")
    suppliername = django_filters.CharFilter(lookup_expr="icontains")
    workorderno = django_filters.CharFilter(lookup_expr="icontains")
    dtc_status = django_filters.CharFilter(field_name="work_order_dtc_appr_status")
    appr_status = django_filters.CharFilter(field_name="work_order_appr_status")
    dt_appr_status = django_filters.CharFilter(field_name="work_order_dt_appr_status")
    send_status = django_filters.CharFilter(field_name="send_status")

    class Meta:
        model = WorkOrderMain
        fields = []


class SalesOrderFilter(django_filters.FilterSet):
    entry_date_after = django_filters.DateFilter(field_name="entry_date", lookup_expr="gte")
    entry_date_before = django_filters.DateFilter(field_name="entry_date", lookup_expr="lte")
    site_id = django_filters.UUIDFilter(field_name="site_id")
    customer_name = django_filters.UUIDFilter(field_name="customer_name")
    approve_status = django_filters.CharFilter(field_name="approve_status")
    work_no = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = SalesOrderStatus
        fields = []


class FreightFilter(django_filters.FilterSet):
    date_after = django_filters.DateFilter(field_name="date", lookup_expr="gte")
    date_before = django_filters.DateFilter(field_name="date", lookup_expr="lte")
    source = django_filters.UUIDFilter(field_name="source")
    freight_no = django_filters.CharFilter(lookup_expr="icontains")
    freight_status = django_filters.CharFilter(field_name="freight_status")

    class Meta:
        model = FreightCreation
        fields = []


class DcEntryFilter(django_filters.FilterSet):
    entry_date_after = django_filters.DateFilter(field_name="entry_date", lookup_expr="gte")
    entry_date_before = django_filters.DateFilter(field_name="entry_date", lookup_expr="lte")
    site_id = django_filters.UUIDFilter(field_name="site_id")
    customer_name = django_filters.UUIDFilter(field_name="customer_name")
    invoice_no = django_filters.CharFilter(lookup_expr="icontains")
    status = django_filters.CharFilter(field_name="status")

    class Meta:
        model = DcEntryForm
        fields = []


class InvoiceFilter(django_filters.FilterSet):
    entry_date_after = django_filters.DateFilter(field_name="entry_date", lookup_expr="gte")
    entry_date_before = django_filters.DateFilter(field_name="entry_date", lookup_expr="lte")
    site_id = django_filters.UUIDFilter(field_name="site_id")
    customer_name = django_filters.UUIDFilter(field_name="customer_name")
    invoice_no = django_filters.CharFilter(lookup_expr="icontains")
    invoice_type = django_filters.CharFilter(field_name="invoice_type")

    class Meta:
        model = InvoiceGeneration
        fields = []


class PayableFilter(django_filters.FilterSet):
    entry_date_after = django_filters.DateFilter(field_name="entry_date", lookup_expr="gte")
    entry_date_before = django_filters.DateFilter(field_name="entry_date", lookup_expr="lte")
    site_id = django_filters.UUIDFilter(field_name="site_id")
    payable_no = django_filters.CharFilter(lookup_expr="icontains")
    appr_status = django_filters.CharFilter(field_name="appr_status")

    class Meta:
        model = PayableEntryMain
        fields = []
