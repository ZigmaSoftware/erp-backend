from decimal import Decimal
from django.db.models import Sum, Q, F, Value, CharField, Count
from django.db.models.functions import TruncMonth, TruncDate, Coalesce
from rest_framework.views import APIView
from rest_framework.response import Response

from apps.sales_transaction.models import (
    DcEntryForm,
    InvoiceGeneration,
    InvoiceSub,
    WorkOrderMain,
    FreightCreation,
    PayableEntryMain,
    ReceivableEntry,
    ConfirmationReceiptDc,
)
from apps.common_master.authentication.header_auth import GatewayHeaderAuthentication


def _parse_date(val):
    from datetime import datetime
    if not val:
        return None
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(val, fmt).date()
        except (ValueError, TypeError):
            continue
    return None


class SupplyChainReportView(APIView):
    authentication_classes = [GatewayHeaderAuthentication]

    def get(self, request):
        qs = DcEntryForm.objects.filter(is_deleted=False, is_active=True)
        from_date = request.query_params.get("from_date")
        to_date = request.query_params.get("to_date")
        item_type = request.query_params.get("item_type")
        item_name = request.query_params.get("item_name")
        customer_name = request.query_params.get("customer_name")
        site_id = request.query_params.get("site_id")
        plant_name = request.query_params.get("plant_name")

        fd = _parse_date(from_date)
        td = _parse_date(to_date)
        if fd:
            qs = qs.filter(entry_date__gte=fd)
        if td:
            qs = qs.filter(entry_date__lte=td)
        if item_name:
            qs = qs.filter(item_name=item_name)
        if customer_name:
            qs = qs.filter(customer_name=customer_name)
        if site_id:
            qs = qs.filter(site_id=site_id)
        if plant_name:
            qs = qs.filter(plant_name=plant_name)

        dc_list = list(qs.order_by("invoice_no").values(
            "unique_id", "invoice_no", "entry_date", "customer_name",
            "item_name", "qty", "site_id", "plant_name",
        ))

        dc_nos = [d["invoice_no"] for d in dc_list]
        invoices = {
            inv.dc_no: inv
            for inv in InvoiceGeneration.objects.filter(
                dc_no__in=dc_nos, is_deleted=False
            )
        } if dc_nos else {}

        for d in dc_list:
            inv = invoices.get(d["invoice_no"])
            if inv:
                d["invoice_number"] = inv.invoice_no
                d["invoice_type"] = inv.invoice_type
                amt = inv.net_amount or Decimal("0")
                if inv.invoice_type == "Others":
                    d["amount"] = str(-amt)
                else:
                    d["amount"] = str(amt)
            else:
                d["invoice_number"] = ""
                d["invoice_type"] = ""
                d["amount"] = "0"
            d["qty_tons"] = str((d.get("qty") or Decimal("0")) / Decimal("1000"))

        return Response({"results": dc_list, "count": len(dc_list)})


class AggregateStockReportView(APIView):
    authentication_classes = [GatewayHeaderAuthentication]

    def get(self, request):
        from_date = _parse_date(request.query_params.get("from_date"))
        to_date = _parse_date(request.query_params.get("to_date"))
        site_id = request.query_params.get("site_id")

        qs = DcEntryForm.objects.filter(is_deleted=False, is_active=True)
        if from_date:
            qs = qs.filter(entry_date__gte=from_date)
        if to_date:
            qs = qs.filter(entry_date__lte=to_date)
        if site_id:
            qs = qs.filter(site_id=site_id)

        results = list(
            qs.values("site_id", "item_name")
            .annotate(
                total_qty=Coalesce(Sum("qty"), Decimal("0")),
                dc_count=Count("unique_id"),
            )
            .order_by("site_id", "item_name")
        )
        for r in results:
            r["total_qty"] = str(r["total_qty"])
            r["total_qty_tons"] = str(Decimal(r["total_qty"]) / Decimal("1000"))

        return Response({"results": results, "count": len(results)})


class AggregateStockPerDayReportView(APIView):
    authentication_classes = [GatewayHeaderAuthentication]

    def get(self, request):
        from_date = _parse_date(request.query_params.get("from_date"))
        to_date = _parse_date(request.query_params.get("to_date"))
        site_id = request.query_params.get("site_id")

        qs = DcEntryForm.objects.filter(is_deleted=False, is_active=True)
        if from_date:
            qs = qs.filter(entry_date__gte=from_date)
        if to_date:
            qs = qs.filter(entry_date__lte=to_date)
        if site_id:
            qs = qs.filter(site_id=site_id)

        results = list(
            qs.values("site_id", "item_name")
            .annotate(
                total_qty=Coalesce(Sum("qty"), Decimal("0")),
                dc_count=Count("unique_id"),
            )
            .order_by("site_id", "item_name")
        )
        for r in results:
            r["date"] = str(r["date"]) if r["date"] else ""
            r["total_qty"] = str(r["total_qty"])
            r["total_qty_tons"] = str(Decimal(r["total_qty"]) / Decimal("1000"))

        return Response({"results": results, "count": len(results)})


class GraphicalRepresentationView(APIView):
    authentication_classes = [GatewayHeaderAuthentication]

    def get(self, request):
        from_date = _parse_date(request.query_params.get("from_date"))
        to_date = _parse_date(request.query_params.get("to_date"))
        site_id = request.query_params.get("site_id")
        item_name = request.query_params.get("item_name")

        qs = DcEntryForm.objects.filter(is_deleted=False, is_active=True)
        if from_date:
            qs = qs.filter(entry_date__gte=from_date)
        if to_date:
            qs = qs.filter(entry_date__lte=to_date)
        if site_id:
            qs = qs.filter(site_id=site_id)
        if item_name:
            qs = qs.filter(item_name=item_name)

        monthly = list(
            qs.annotate(month=TruncMonth("entry_date"))
            .values("month", "item_name")
            .annotate(total_qty=Coalesce(Sum("qty"), Decimal("0")))
            .order_by("month", "item_name")
        )
        for r in monthly:
            r["month"] = str(r["month"]) if r["month"] else ""
            r["total_qty"] = str(r["total_qty"])
            r["total_qty_tons"] = str(Decimal(r["total_qty"]) / Decimal("1000"))

        return Response({"results": monthly, "count": len(monthly)})


class SiteWiseDisposalReportView(APIView):
    authentication_classes = [GatewayHeaderAuthentication]

    def get(self, request):
        from_date = _parse_date(request.query_params.get("from_date"))
        to_date = _parse_date(request.query_params.get("to_date"))
        site_id = request.query_params.get("site_id")

        dc_qs = DcEntryForm.objects.filter(is_deleted=False, is_active=True)
        if from_date:
            dc_qs = dc_qs.filter(entry_date__gte=from_date)
        if to_date:
            dc_qs = dc_qs.filter(entry_date__lte=to_date)
        if site_id:
            dc_qs = dc_qs.filter(site_id=site_id)

        dc_entries = list(dc_qs.values(
            "unique_id", "invoice_no", "entry_date", "site_id",
            "customer_name", "item_name", "qty",
        ))

        dc_nos = [d["invoice_no"] for d in dc_entries]
        invoice_map = {}
        if dc_nos:
            for inv in InvoiceGeneration.objects.filter(
                dc_no__in=dc_nos, is_deleted=False
            ):
                invoice_map.setdefault(inv.dc_no, []).append(inv)

        for d in dc_entries:
            invs = invoice_map.get(d["invoice_no"], [])
            payable = sum(
                float(inv.net_amount or 0) for inv in invs
                if inv.invoice_type == "Others"
            )
            receivable = sum(
                float(inv.net_amount or 0) for inv in invs
                if inv.invoice_type == "Invoice"
            )
            freight = sum(
                float(inv.freight_amount or 0) for inv in invs
            )
            d["payable_amount"] = str(payable)
            d["receivable_amount"] = str(receivable)
            d["freight_amount"] = str(freight)
            d["qty_tons"] = str(Decimal(d.get("qty") or "0") / Decimal("1000"))

        return Response({"results": dc_entries, "count": len(dc_entries)})


class SiteWiseDisposalComparisonView(APIView):
    authentication_classes = [GatewayHeaderAuthentication]

    def get(self, request):
        from_date = _parse_date(request.query_params.get("from_date"))
        to_date = _parse_date(request.query_params.get("to_date"))
        site_id = request.query_params.get("site_id")

        qs = DcEntryForm.objects.filter(is_deleted=False, is_active=True)
        if from_date:
            qs = qs.filter(entry_date__gte=from_date)
        if to_date:
            qs = qs.filter(entry_date__lte=to_date)
        if site_id:
            qs = qs.filter(site_id=site_id)

        monthly = list(
            qs.annotate(month=TruncMonth("entry_date"))
            .values("month", "site_id", "item_name")
            .annotate(
                total_qty=Coalesce(Sum("qty"), Decimal("0")),
                dc_count=Count("unique_id"),
            )
            .order_by("month", "site_id")
        )
        for r in monthly:
            r["month"] = str(r["month"]) if r["month"] else ""
            r["total_qty"] = str(r["total_qty"])
            r["total_qty_tons"] = str(Decimal(r["total_qty"]) / Decimal("1000"))

        return Response({"results": monthly, "count": len(monthly)})


class ConsolidatedMonthlySiteWiseReportView(APIView):
    authentication_classes = [GatewayHeaderAuthentication]

    def get(self, request):
        from_date = _parse_date(request.query_params.get("from_date"))
        to_date = _parse_date(request.query_params.get("to_date"))
        site_id = request.query_params.get("site_id")

        qs = DcEntryForm.objects.filter(is_deleted=False, is_active=True)
        if from_date:
            qs = qs.filter(entry_date__gte=from_date)
        if to_date:
            qs = qs.filter(entry_date__lte=to_date)
        if site_id:
            qs = qs.filter(site_id=site_id)

        monthly = list(
            qs.annotate(month=TruncMonth("entry_date"))
            .values("month", "site_id")
            .annotate(
                total_qty=Coalesce(Sum("qty"), Decimal("0")),
                dc_count=Count("unique_id"),
            )
            .order_by("-month", "site_id")
        )
        for r in monthly:
            r["month"] = str(r["month"]) if r["month"] else ""
            r["total_qty"] = str(r["total_qty"])
            r["total_qty_tons"] = str(Decimal(r["total_qty"]) / Decimal("1000"))

        return Response({"results": monthly, "count": len(monthly)})


class PayableReceivableTrackerView(APIView):
    authentication_classes = [GatewayHeaderAuthentication]

    def get(self, request):
        from django.db.models import Count
        customer_name = request.query_params.get("customer_name")
        site_id = request.query_params.get("site_id")

        dc_qs = DcEntryForm.objects.filter(is_deleted=False, is_active=True)
        if customer_name:
            dc_qs = dc_qs.filter(customer_name=customer_name)
        if site_id:
            dc_qs = dc_qs.filter(site_id=site_id)

        dc_entries = list(dc_qs.values(
            "unique_id", "invoice_no", "entry_date", "site_id",
            "customer_name", "item_name", "qty",
        ))

        dc_nos = [d["invoice_no"] for d in dc_entries]
        invoice_map = {}
        if dc_nos:
            for inv in InvoiceGeneration.objects.filter(
                dc_no__in=dc_nos, is_deleted=False
            ):
                invoice_map.setdefault(inv.dc_no, []).append(inv)

        for d in dc_entries:
            invs = invoice_map.get(d["invoice_no"], [])
            payable = sum(
                float(inv.net_amount or 0) for inv in invs
                if inv.invoice_type == "Others"
            )
            receivable = sum(
                float(inv.net_amount or 0) for inv in invs
                if inv.invoice_type == "Invoice"
            )
            d["payable_amount"] = str(payable)
            d["receivable_amount"] = str(receivable)
            d["balance"] = str(receivable - payable)
            d["qty_tons"] = str(Decimal(d.get("qty") or "0") / Decimal("1000"))

        return Response({"results": dc_entries, "count": len(dc_entries)})


class CustomerCreationReportView(APIView):
    authentication_classes = [GatewayHeaderAuthentication]

    def get(self, request):
        from apps.sales_master.models import CustomerCreationMaster
        customer_name = request.query_params.get("customer_name")
        site_id = request.query_params.get("site_id")

        qs = CustomerCreationMaster.objects.filter(is_deleted=False, is_active=True)
        if customer_name:
            qs = qs.filter(
                Q(customer_name__icontains=customer_name) |
                Q(unique_id=customer_name) if customer_name else Q()
            )
        if site_id:
            qs = qs.filter(site_id=site_id)

        results = list(qs.values(
            "unique_id", "customer_id", "customer_name",
            "contact_person", "mobile_no", "email_id",
            "site_id", "address", "opening_balance",
        ).order_by("customer_name")[:500])

        return Response({"results": results, "count": len(results)})


class ConfirmationReceiptReportView(APIView):
    authentication_classes = [GatewayHeaderAuthentication]

    def get(self, request):
        from_date = _parse_date(request.query_params.get("from_date"))
        to_date = _parse_date(request.query_params.get("to_date"))
        site_id = request.query_params.get("site_id")

        qs = ConfirmationReceiptDc.objects.filter(is_deleted=False, is_active=True)
        if from_date:
            qs = qs.filter(entry_date__gte=from_date)
        if to_date:
            qs = qs.filter(entry_date__lte=to_date)
        if site_id:
            qs = qs.filter(site_id=site_id)

        results = list(qs.values(
            "unique_id", "dc_no", "entry_date", "site_id",
            "customer_name", "item_name", "total_qty",
            "received_qty", "status",
        ).order_by("-entry_date")[:500])

        return Response({"results": results, "count": len(results)})


class WorkOrderStatusReportView(APIView):
    authentication_classes = [GatewayHeaderAuthentication]

    def get(self, request):
        from_date = _parse_date(request.query_params.get("from_date"))
        to_date = _parse_date(request.query_params.get("to_date"))
        customer_name = request.query_params.get("customer_name")
        site_id = request.query_params.get("site_id")
        status = request.query_params.get("status")

        qs = WorkOrderMain.objects.filter(is_deleted=False, is_active=True)
        if from_date:
            qs = qs.filter(entry_date__gte=from_date)
        if to_date:
            qs = qs.filter(entry_date__lte=to_date)
        if customer_name:
            qs = qs.filter(customer_name=customer_name)
        if site_id:
            qs = qs.filter(site_id=site_id)
        if status:
            qs = qs.filter(status=status)

        results = list(qs.values(
            "unique_id", "work_order_no", "entry_date", "customer_name",
            "site_id", "item_name", "qty", "rate", "total_amount",
            "status", "approval_status",
        ).order_by("-entry_date")[:500])

        for r in results:
            r["entry_date"] = str(r["entry_date"]) if r["entry_date"] else ""

        return Response({"results": results, "count": len(results)})


class MBSReportView(APIView):
    authentication_classes = [GatewayHeaderAuthentication]

    def get(self, request):
        from_date = _parse_date(request.query_params.get("from_date"))
        to_date = _parse_date(request.query_params.get("to_date"))
        site_id = request.query_params.get("site_id")

        qs = DcEntryForm.objects.filter(is_deleted=False, is_active=True)
        if from_date:
            qs = qs.filter(entry_date__gte=from_date)
        if to_date:
            qs = qs.filter(entry_date__lte=to_date)
        if site_id:
            qs = qs.filter(site_id=site_id)

        results = list(
            qs.values("site_id", "item_name")
            .annotate(
                total_qty=Coalesce(Sum("qty"), Decimal("0")),
                dc_count=Count("unique_id"),
            )
            .order_by("site_id", "item_name")
        )

        for r in site_outward:
            r["total_qty"] = str(r["total_qty"])
            r["total_qty_tons"] = str(Decimal(r["total_qty"]) / Decimal("1000"))

        return Response({"results": site_outward, "count": len(site_outward)})


class RDFTrackerReportView(APIView):
    authentication_classes = [GatewayHeaderAuthentication]

    def get(self, request):
        from_date = _parse_date(request.query_params.get("from_date"))
        to_date = _parse_date(request.query_params.get("to_date"))
        site_id = request.query_params.get("site_id")

        qs = DcEntryForm.objects.filter(is_deleted=False, is_active=True)
        if from_date:
            qs = qs.filter(entry_date__gte=from_date)
        if to_date:
            qs = qs.filter(entry_date__lte=to_date)
        if site_id:
            qs = qs.filter(site_id=site_id)

        monthly = list(
            qs.annotate(month=TruncMonth("entry_date"))
            .values("month", "site_id", "item_name")
            .annotate(
                total_qty=Coalesce(Sum("qty"), Decimal("0")),
                dc_count=Count("unique_id"),
            )
            .order_by("-month", "site_id")
        )
        for r in monthly:
            r["month"] = str(r["month"]) if r["month"] else ""
            r["total_qty"] = str(r["total_qty"])
            r["total_qty_tons"] = str(Decimal(r["total_qty"]) / Decimal("1000"))

        return Response({"results": monthly, "count": len(monthly)})


class ICWDetailsReportView(APIView):
    authentication_classes = [GatewayHeaderAuthentication]

    def get(self, request):
        from_date = _parse_date(request.query_params.get("from_date"))
        to_date = _parse_date(request.query_params.get("to_date"))
        site_id = request.query_params.get("site_id")
        customer_name = request.query_params.get("customer_name")

        qs = DcEntryForm.objects.filter(is_deleted=False, is_active=True)
        if from_date:
            qs = qs.filter(entry_date__gte=from_date)
        if to_date:
            qs = qs.filter(entry_date__lte=to_date)
        if site_id:
            qs = qs.filter(site_id=site_id)
        if customer_name:
            qs = qs.filter(customer_name=customer_name)

        results = list(qs.values(
            "unique_id", "invoice_no", "entry_date", "customer_name",
            "item_name", "site_id", "qty",
        ).order_by("-entry_date")[:500])

        for r in results:
            r["entry_date"] = str(r["entry_date"]) if r["entry_date"] else ""
            r["qty"] = str(r["qty"])
            r["qty_tons"] = str(Decimal(r["qty"]) / Decimal("1000"))

        return Response({"results": results, "count": len(results)})


class OthersAggregateComparisonReportView(APIView):
    authentication_classes = [GatewayHeaderAuthentication]

    def get(self, request):
        from_date = _parse_date(request.query_params.get("from_date"))
        to_date = _parse_date(request.query_params.get("to_date"))
        site_id = request.query_params.get("site_id")

        qs = DcEntryForm.objects.filter(is_deleted=False, is_active=True)
        if from_date:
            qs = qs.filter(entry_date__gte=from_date)
        if to_date:
            qs = qs.filter(entry_date__lte=to_date)
        if site_id:
            qs = qs.filter(site_id=site_id)

        monthly = list(
            qs.annotate(month=TruncMonth("entry_date"))
            .values("month", "site_id", "item_name")
            .annotate(
                total_qty=Coalesce(Sum("qty"), Decimal("0")),
                dc_count=Count("unique_id"),
            )
            .order_by("-month", "site_id")
        )
        for r in monthly:
            r["month"] = str(r["month"]) if r["month"] else ""
            r["total_qty"] = str(r["total_qty"])
            r["total_qty_tons"] = str(Decimal(r["total_qty"]) / Decimal("1000"))

        return Response({"results": monthly, "count": len(monthly)})

