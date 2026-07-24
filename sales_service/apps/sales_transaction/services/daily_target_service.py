from django.db import transaction
from rest_framework import serializers

from apps.sales_transaction.models.daily_target_disposal import DailyTargetDisposalMain, DailyTargetDisposalSub
from apps.sales_shared.services.number_generation import generate_daily_target_number


class DailyTargetService:

    @staticmethod
    def _check_duplicate(data, exclude_pk=None):
        # PHP blocks a second entry for the same site_id + entry_date
        # (daily_target_entry_disposal/model/daily_target_entry_disposal_form.php:208-215).
        qs = DailyTargetDisposalMain.objects.filter(
            site_id=data["site_id"],
            entry_date=data["entry_date"],
            is_deleted=False,
        )
        if exclude_pk is not None:
            qs = qs.exclude(pk=exclude_pk)
        if qs.exists():
            raise serializers.ValidationError(
                "A daily target entry already exists for this site and date."
            )

    @classmethod
    @transaction.atomic
    def create(cls, data):
        sub_items_data = data.pop("sub_items", [])
        site_code = data.pop("site_code", "")
        cls._check_duplicate(data)
        main = DailyTargetDisposalMain.objects.create(
            entry_no=generate_daily_target_number(site_code),
            site_id=data["site_id"],
            entry_date=data["entry_date"],
            created_by=data.get("created_by", ""),
        )
        for sub in sub_items_data:
            DailyTargetDisposalSub.objects.create(main=main, **sub)
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
                DailyTargetDisposalSub.objects.create(main=instance, **sub)
        return instance

    @classmethod
    def delete(cls, instance):
        instance.delete()
