from datetime import datetime

from django.db import transaction

from apps.sales_shared.models.document_number_sequence import DocumentNumberSequence


def _next_number(prefix, site_code, year_month, padding=4):
    with transaction.atomic():
        seq, _ = DocumentNumberSequence.objects.select_for_update().get_or_create(
            prefix=prefix, site_code=site_code, year_month=year_month,
            defaults={"last_sequence": 0},
        )
        seq.last_sequence += 1
        seq.save(update_fields=["last_sequence", "updated_at"])
        return str(seq.last_sequence).zfill(padding)


def generate_work_order_number(site_code="HO"):
    """WO-{site_code}-{YYMM}-NNNN"""
    ym = datetime.now().strftime("%y%m")
    return f"WO-{site_code}-{ym}-{_next_number('WO', site_code, ym)}"


def generate_dc_number(site_code="ZG"):
    """{site_code}-DC-{YYMM}-NNNN"""
    ym = datetime.now().strftime("%y%m")
    return f"{site_code}-DC-{ym}-{_next_number('DC', site_code, ym)}"


def generate_invoice_number(site_code="ZG", invoice_type="Invoice"):
    now = datetime.now()
    if invoice_type == "Invoice":
        if now.month >= 4:
            ys, ye = now.year, now.year + 1
        else:
            ys, ye = now.year - 1, now.year
        ym = f"{str(ys)[-2:]}-{str(ye)[-2:]}"
        n = _next_number("INV", site_code, ym)
        return f"{site_code}/{ym}/{n}"
    else:
        ym = now.strftime("%y%m")
        n = _next_number("EST", "", ym)
        return f"EST-{ym}-{n}"


def generate_payable_number():
    """PAY-{YYMM}-NNNN"""
    ym = datetime.now().strftime("%y%m")
    return f"PAY-{ym}-{_next_number('PAY', '', ym)}"


def generate_freight_number():
    """FC-{YYMM}-NNNN"""
    ym = datetime.now().strftime("%y%m")
    return f"FC-{ym}-{_next_number('FC', '', ym)}"


def _quotation_style_number(prefix, site_code="", padding=4):
    """
    Day-Product quotation/entry numbers.

    Legacy PHP format (aggregate_quotation_entry/entry_no.php,
    scrap_quotation_entry/entry_no.php, daily_target_entry_disposal/dte_entry_no.php):
        {PREFIX}-{site_invoice_head}-{YYMM}-{NNNN}   (per-site, resets each calendar year)
    PHP server-side fallback (create.php) when no site head is available:
        {PREFIX}-{YYMM}-{NNNN}

    The site "invoice head" is master data owned outside this service, so callers
    pass it in as ``site_code`` when known; otherwise the head-less fallback format
    is used. The running sequence is keyed by (prefix, site_code, year) so it resets
    per calendar year per site, and is allocated atomically via ``_next_number``.
    """
    now = datetime.now()
    yymm = now.strftime("%y%m")
    year = now.strftime("%y")
    seq = _next_number(prefix, site_code or "", year, padding=padding)
    if site_code:
        return f"{prefix}-{site_code}-{yymm}-{seq}"
    return f"{prefix}-{yymm}-{seq}"


def generate_aggregate_quotation_number(site_code=""):
    """AGQUT-[{site}-]{YYMM}-NNNN"""
    return _quotation_style_number("AGQUT", site_code)


def generate_scrap_quotation_number(site_code=""):
    """SQUT-[{site}-]{YYMM}-NNNN"""
    return _quotation_style_number("SQUT", site_code)


def generate_daily_target_number(site_code=""):
    """DIS-DTE-[{site}-]{YYMM}-NNNN"""
    return _quotation_style_number("DIS-DTE", site_code)


def generate_aggregate_entry_number():
    """
    Aggregate Entry (legacy scrap_entry): SEN-{YYMM}-NNNN, no site head,
    resets each calendar year (scrap_entry_form/create.php:69-81).
    """
    now = datetime.now()
    yymm = now.strftime("%y%m")
    year = now.strftime("%y")
    return f"SEN-{yymm}-{_next_number('SEN', '', year)}"


def generate_transport_entry_number(site_code=""):
    """
    AFR Transport Entry (legacy trans_appr_entry): ZEP-[{site}-]{YYYYMM}-NNNN,
    per-site, resets each calendar year (trans_appr_entry/create.php:60-67).
    """
    now = datetime.now()
    yyyymm = now.strftime("%Y%m")
    year = now.strftime("%Y")
    seq = _next_number("ZEP", site_code or "", year)
    if site_code:
        return f"ZEP-{site_code}-{yyyymm}-{seq}"
    return f"ZEP-{yyyymm}-{seq}"
