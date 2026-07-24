from django.db import transaction

from apps.sales_transaction.models.aggregate_entry import AggregateEntryMain, AggregateEntrySub
from apps.sales_shared.services.number_generation import generate_aggregate_entry_number


class AggregateEntryService:
    """Legacy scrap_entry / scrap_entry_sub ("Aggregate Entry")."""

    @classmethod
    @transaction.atomic
    def create(cls, data):
        sub_items_data = data.pop("sub_items", [])
        data.pop("site_code", None)  # not used by SEN numbering, accepted for API symmetry
        main = AggregateEntryMain.objects.create(
            scrap_no=generate_aggregate_entry_number(),
            entry_date=data["entry_date"],
            site_id=data["site_id"],
            plant_id=data.get("plant_id"),
            plant_name=data.get("plant_name", ""),
            description=data.get("description", ""),
            created_by=data.get("created_by", ""),
        )
        for sub in sub_items_data:
            AggregateEntrySub.objects.create(main=main, **sub)
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
                AggregateEntrySub.objects.create(main=instance, **sub)
        return instance
