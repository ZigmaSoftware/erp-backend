import re

from django.db import models
from django.db.models import Q

from apps.sales_master.utils.random_code_gen import (
    generate_random_no,
    generate_random_sc,
)
from shared.base_models import BaseMaster


class RdfInertsPercEntry(BaseMaster):
    class ItemType(models.TextChoices):
        RDF = "RDF", "RDF"
        INERTS = "Inerts", "Inerts"

    random_sc = models.CharField(max_length=12, unique=True, blank=True)
    random_no = models.CharField(max_length=5, unique=True, blank=True)
    ri_perc_entry_no = models.CharField(max_length=40, unique=True, blank=True)
    site_name = models.CharField(max_length=150)
    perc_date = models.DateField()
    perc_item_name = models.CharField(max_length=20, choices=ItemType.choices)
    perc_item_percentage = models.DecimalField(max_digits=6, decimal_places=2)
    perc_status = models.BooleanField(default=True)

    class Meta:
        db_table = "rdf_inerts_perc_entry"
        ordering = ["-perc_date", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["random_sc", "random_no", "ri_perc_entry_no"],
                condition=Q(is_deleted=False),
                name="uq_rdf_inerts_perc_entry_ref_active",
            ),
        ]

    def __str__(self):
        return self.ri_perc_entry_no or "RDF & Inerts Percentage Entry"

    @staticmethod
    def build_site_code(site):
        source = getattr(site, "screen_name", None) or getattr(site, "site_name", site)
        code = re.sub(r"[^A-Za-z0-9]", "", str(source).upper())
        return (code[:3] or "SIT").ljust(3, "X")

    def generate_entry_no(self):
        site_code = self.build_site_code(self.site_name)
        year_month = self.perc_date.strftime("%y%m")
        prefix = f"Perc-RI-{site_code}-{year_month}-"
        serial = (
            RdfInertsPercEntry.objects.filter(
                ri_perc_entry_no__startswith=prefix,
                is_deleted=False,
            ).count()
            + 1
        )
        candidate = f"{prefix}{serial:04d}"
        while RdfInertsPercEntry.objects.filter(
            ri_perc_entry_no=candidate,
            is_deleted=False,
        ).exists():
            serial += 1
            candidate = f"{prefix}{serial:04d}"
        return candidate

    def save(self, *args, **kwargs):
        if not self.random_no:
            self.random_no = generate_random_no(RdfInertsPercEntry)
        if not self.random_sc:
            self.random_sc = generate_random_sc(RdfInertsPercEntry)
        if not self.ri_perc_entry_no:
            self.ri_perc_entry_no = self.generate_entry_no()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.is_active = False
        self.save(update_fields=["is_deleted", "is_active"])


class RdfInertsPercEntrySub(BaseMaster):
    class ItemType(models.TextChoices):
        RDF = "RDF", "RDF"
        INERTS = "Inerts", "Inerts"

    random_sc = models.CharField(max_length=12)
    random_no = models.CharField(max_length=5)
    ri_perc_entry_no = models.CharField(max_length=40)
    site_name = models.CharField(max_length=150)
    perc_date = models.DateField()
    perc_item_name = models.CharField(max_length=20, choices=ItemType.choices)
    perc_item_percentage = models.DecimalField(max_digits=6, decimal_places=2)
    perc_status = models.BooleanField(default=True)

    class Meta:
        db_table = "rdf_inerts_perc_entry_sub"
        ordering = ["perc_date", "id"]
        indexes = [
            models.Index(
                fields=["random_sc", "random_no", "ri_perc_entry_no"],
                name="idx_ri_perc_sub_ref",
            ),
        ]

    def __str__(self):
        return f"{self.ri_perc_entry_no} - {self.perc_item_name}"

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.is_active = False
        self.save(update_fields=["is_deleted", "is_active"])
