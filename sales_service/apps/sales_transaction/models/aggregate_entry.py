import uuid

from django.db import models
from django.db.models import Q

from apps.sales_master.utils.random_code_gen import (
    generate_random_no,
    generate_random_sc,
)
from apps.sales_shared.services.number_generation import generate_aggregate_entry_number


class AggregateEntryMain(models.Model):
    """
    Legacy: scrap_entry / scrap_entry_sub ("Aggregate Entry").

    A main record is identified by the composite reference
    (random_no, random_sc, scrap_no). Sub rows carry the same reference
    triple instead of a foreign key, mirroring ``rdf_inerts_perc_entry``.

    ``site_name`` / ``plant_name`` store the Master Service **IDs** (not the
    display names); the client resolves the display names from Master
    Service. ``scrap_no`` holds the legacy SEN-{YYMM}-NNNN document number.
    """

    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    random_no = models.CharField(max_length=5, blank=True, default="")
    random_sc = models.CharField(max_length=40, blank=True, default="")
    scrap_no = models.CharField(max_length=50, blank=True, help_text="Legacy SEN-{YYMM}-NNNN number")

    entry_date = models.DateField()
    site_name = models.CharField(max_length=150, help_text="Site master ID")
    plant_name = models.CharField(max_length=150, blank=True, default="", help_text="Plant master ID")
    description = models.TextField(blank=True, default="")

    ipaddress = models.CharField(max_length=45, blank=True, default="")
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=40, blank=True, default="")
    updated_by = models.CharField(max_length=40, blank=True, default="")

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["random_no", "random_sc", "scrap_no"],
                condition=Q(is_deleted=False),
                name="uq_aggregate_entry_ref_active",
            ),
        ]
        indexes = [
            models.Index(fields=["random_no"], name="idx_agg_entry_random_no"),
            models.Index(fields=["random_sc"], name="idx_agg_entry_random_sc"),
            models.Index(fields=["scrap_no"], name="idx_agg_entry_scrap_no"),
            models.Index(fields=["entry_date"], name="idx_agg_entry_date"),
            models.Index(fields=["site_name"], name="idx_agg_entry_site"),
            models.Index(fields=["plant_name"], name="idx_agg_entry_plant"),
        ]

    def __str__(self):
        return self.scrap_no or "Aggregate Entry"

    @property
    def sub_items(self):
        return AggregateEntrySub.objects.filter(
            random_no=self.random_no,
            random_sc=self.random_sc,
            scrap_no=self.scrap_no,
        )

    def save(self, *args, **kwargs):
        if not self.random_no:
            self.random_no = generate_random_no(AggregateEntryMain)
        if not self.random_sc:
            self.random_sc = generate_random_sc(AggregateEntryMain)
        if not self.scrap_no:
            self.scrap_no = generate_aggregate_entry_number()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.is_active = False
        self.save(update_fields=["is_deleted", "is_active"])
        self.sub_items.filter(is_deleted=False).update(is_deleted=True, is_active=False)


class AggregateEntrySub(models.Model):
    """
    Sub row of an Aggregate Entry. Associated with its main record through the
    (random_no, random_sc, scrap_no) reference triple, which is shared by all
    sub rows of one main entry along with entry_date / site_name / plant_name.

    ``item_name`` stores the Item/By-Product master **ID**.
    """

    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    random_no = models.CharField(max_length=5, blank=True, default="")
    random_sc = models.CharField(max_length=40, blank=True, default="")
    scrap_no = models.CharField(max_length=50, blank=True, default="")
    entry_date = models.DateField(null=True, blank=True)
    site_name = models.CharField(max_length=150, blank=True, default="", help_text="Site master ID")
    plant_name = models.CharField(max_length=150, blank=True, default="", help_text="Plant master ID")

    item_name = models.CharField(max_length=150, blank=True, default="", help_text="Item/By-Product master ID")
    # In legacy PHP `stock` is auto-fetched from MBS percentage data
    # (mbs_percent_sublist), owned by another module and not present in
    # sales_service; accepted as input here until an MBS read-model exists.
    stock = models.DecimalField(max_digits=15, decimal_places=3, default=0)
    receipt = models.DecimalField(max_digits=15, decimal_places=3, default=0)
    remarks = models.TextField(blank=True, default="")

    ipaddress = models.CharField(max_length=45, blank=True, default="")
    # Legacy scrap_entry_sub merge bookkeeping (retained for parity; default 0).
    mu_status = models.IntegerField(default=0)
    merge_update = models.IntegerField(default=0)
    merge_id = models.CharField(max_length=50, blank=True, default="")

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=40, blank=True, default="")
    updated_by = models.CharField(max_length=40, blank=True, default="")

    class Meta:
        ordering = ["id"]
        indexes = [
            models.Index(
                fields=["random_no", "random_sc", "scrap_no"],
                name="idx_agg_entry_sub_ref",
            ),
            models.Index(fields=["entry_date"], name="idx_agg_entry_sub_date"),
        ]

    def __str__(self):
        return f"{self.item_name} - {self.receipt}"

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.is_active = False
        self.save(update_fields=["is_deleted", "is_active"])
