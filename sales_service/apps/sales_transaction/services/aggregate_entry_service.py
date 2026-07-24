from django.db import transaction

from apps.sales_transaction.models.aggregate_entry import (
    AggregateEntryMain,
    AggregateEntrySub,
)


class AggregateEntryService:
    """
    Legacy scrap_entry / scrap_entry_sub ("Aggregate Entry").

    One main record (identified by the composite reference
    random_no + random_sc + scrap_no) owns many sub rows. Sub rows carry the
    same reference triple, entry_date, site_name and plant_name as the main
    record -- mirroring the ``rdf_inerts_perc_entry`` save mechanism.
    """

    @staticmethod
    def _build_sub_rows(main, sub_items_data, username):
        rows = []
        for sub in sub_items_data:
            rows.append(
                AggregateEntrySub(
                    random_no=main.random_no,
                    random_sc=main.random_sc,
                    scrap_no=main.scrap_no,
                    entry_date=main.entry_date,
                    site_name=main.site_name,
                    plant_name=main.plant_name,
                    item_name=sub["item_name"],
                    stock=sub.get("stock", 0) or 0,
                    receipt=sub["receipt"],
                    remarks=sub.get("remarks", ""),
                    created_by=username or "",
                )
            )
        return rows

    @classmethod
    @transaction.atomic
    def create(cls, data):
        sub_items_data = data.pop("sub_items", [])
        username = data.get("created_by", "")
        main = AggregateEntryMain.objects.create(
            entry_date=data["entry_date"],
            site_name=data["site_name"],
            plant_name=data.get("plant_name", ""),
            description=data.get("description", ""),
            created_by=username,
        )
        AggregateEntrySub.objects.bulk_create(
            cls._build_sub_rows(main, sub_items_data, username)
        )
        return main

    @classmethod
    @transaction.atomic
    def update(cls, instance, data):
        sub_items_data = data.pop("sub_items", None)
        username = data.get("updated_by", "")

        # Preserve the original reference triple; update only editable fields.
        for field in ("entry_date", "site_name", "plant_name", "description"):
            if field in data:
                setattr(instance, field, data[field])
        instance.updated_by = username
        instance.save()

        if sub_items_data is not None:
            # Legacy mu_status/merge bookkeeping: mark the superseded rows.
            instance.sub_items.filter(is_deleted=False).update(
                is_deleted=True,
                is_active=False,
                mu_status=1,
                updated_by=username,
            )
            AggregateEntrySub.objects.bulk_create(
                cls._build_sub_rows(instance, sub_items_data, username)
            )
        return instance
