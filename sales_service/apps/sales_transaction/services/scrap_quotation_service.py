from django.db import transaction
from rest_framework import serializers

from apps.sales_transaction.models.scrap_quotation import ScrapQuotationMain, ScrapQuotationSub
from apps.sales_shared.services.number_generation import generate_scrap_quotation_number


class ScrapQuotationService:

    @staticmethod
    def _check_duplicate(data, exclude_pk=None):
        # PHP blocks duplicate party_name + party_mobile_no + site_id + quote_month
        # (scrap_quotation_entry/model/scrap_quotation_entry_form.php:280-289).
        qs = ScrapQuotationMain.objects.filter(
            party_name=data["party_name"],
            party_mobile_no=data["party_mobile_no"],
            site_id=data["site_id"],
            quote_month=data["quote_month"],
            is_deleted=False,
        )
        if exclude_pk is not None:
            qs = qs.exclude(pk=exclude_pk)
        if qs.exists():
            raise serializers.ValidationError(
                "A quotation already exists for this party, mobile number, site and month."
            )

    @classmethod
    @transaction.atomic
    def create(cls, data):
        sub_items_data = data.pop("sub_items", [])
        site_code = data.pop("site_code", "")
        cls._check_duplicate(data)
        main = ScrapQuotationMain.objects.create(
            quote_entry_no=generate_scrap_quotation_number(site_code),
            party_name=data["party_name"],
            party_mobile_no=data["party_mobile_no"],
            party_address=data.get("party_address", ""),
            site_id=data["site_id"],
            quote_month=data["quote_month"],
            main_description=data.get("main_description", ""),
            quote_file=data.get("quote_file", ""),
            created_by=data.get("created_by", ""),
        )
        for sub in sub_items_data:
            ScrapQuotationSub.objects.create(main=main, **sub)
        return main

    @classmethod
    @transaction.atomic
    def update(cls, instance, data):
        sub_items_data = data.pop("sub_items", None)
        data.pop("site_code", None)
        for k, v in data.items():
            setattr(instance, k, v)
        instance.save()
        if sub_items_data is not None:
            instance.sub_items.filter(is_deleted=False).update(is_deleted=True, is_active=False)
            for sub in sub_items_data:
                sub.pop("unique_id", None)
                ScrapQuotationSub.objects.create(main=instance, **sub)
        return instance

    @classmethod
    def delete(cls, instance):
        instance.delete()
