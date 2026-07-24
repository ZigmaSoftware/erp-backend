from django.db import transaction
from rest_framework import serializers

from apps.sales_transaction.models.afr_transport_entry import AfrTransportEntryMain, AfrTransportEntrySub
from apps.sales_shared.services.number_generation import generate_transport_entry_number


class AfrTransportEntryService:
    """Legacy trans_appr_entry / trans_appr_entry_sublist ("AFR Transport Entry")."""

    @staticmethod
    def _check_duplicate(data, exclude_pk=None):
        # PHP blocks a duplicate site + customer + transporter
        # (trans_appr_entry/model/trans_appr_entry_1.php:247).
        qs = AfrTransportEntryMain.objects.filter(
            site_id=data["site_id"],
            customer_id=data.get("customer_id"),
            transporter_id=data.get("transporter_id"),
            is_deleted=False,
        )
        if exclude_pk is not None:
            qs = qs.exclude(pk=exclude_pk)
        if qs.exists():
            raise serializers.ValidationError(
                "An entry already exists for this site, customer and transporter."
            )

    @classmethod
    @transaction.atomic
    def create(cls, data):
        sub_items_data = data.pop("sub_items", [])
        site_code = data.pop("site_code", "")
        cls._check_duplicate(data)
        main = AfrTransportEntryMain.objects.create(
            trans_appr_no=generate_transport_entry_number(site_code),
            entry_date=data["entry_date"],
            site_id=data["site_id"],
            customer_id=data.get("customer_id"),
            customer_name=data.get("customer_name", ""),
            transporter_id=data.get("transporter_id"),
            transporter_name=data.get("transporter_name", ""),
            cpcr_no=data.get("cpcr_no", ""),
            remarks=data.get("remarks", ""),
            created_by=data.get("created_by", ""),
        )
        for sub in sub_items_data:
            AfrTransportEntrySub.objects.create(main=main, **sub)
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
                AfrTransportEntrySub.objects.create(main=instance, **sub)
        return instance
