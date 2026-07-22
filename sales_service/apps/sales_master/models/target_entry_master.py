from django.db import models
from django.db.models import Sum

from shared.base_models import BaseMaster

from apps.sales_master.utils.random_code_gen import generate_random_no, generate_random_sc
from apps.sales_master.utils.target_entry_no_gen import generate_target_entry_no


class TargetEntryMaster(BaseMaster):

    target_no = models.CharField(max_length=20, unique=True, blank=True)
    entry_month = models.DateField()

    # Master Service Site `unique_id` (no DB-level FK - see SALES_SERVICE_README.md).
    site_id = models.UUIDField()

    random_no = models.CharField(max_length=5, unique=True, blank=True)
    random_sc = models.CharField(max_length=12, unique=True, blank=True)

    # Denormalized sums over active items, kept in sync whenever a
    # TargetEntryItem is added, updated, or (soft-)deleted.
    tot_target = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    tot_expense = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    tot_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.target_no

    def save(self, *args, **kwargs):
        if not self.target_no:
            self.target_no = generate_target_entry_no(TargetEntryMaster)
        if not self.random_no:
            self.random_no = generate_random_no(TargetEntryMaster)
        if not self.random_sc:
            self.random_sc = generate_random_sc(TargetEntryMaster)
        super().save(*args, **kwargs)

    def recalculate_totals(self):
        aggregates = self.items.filter(is_deleted=False).aggregate(
            target=Sum("target_qty"),
            expense=Sum("expense_amount"),
            revenue=Sum("revenue_amount"),
        )
        self.tot_target = aggregates["target"] or 0
        self.tot_expense = aggregates["expense"] or 0
        self.tot_revenue = aggregates["revenue"] or 0
        self.save(update_fields=["tot_target", "tot_expense", "tot_revenue"])

    def delete(self, *args, **kwargs):
        """
        Soft delete (cascades to line items)
        """
        self.is_deleted = True
        self.is_active = False
        self.save(update_fields=["is_deleted", "is_active"])
        self.items.filter(is_deleted=False).update(is_deleted=True, is_active=False)
