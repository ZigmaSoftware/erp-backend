from decimal import Decimal

from django.db import models

from apps.common_master.models.city import City
from apps.common_master.models.country import Country
from apps.common_master.models.district import District
from apps.common_master.models.site import Site
from apps.common_master.models.state import State
from apps.sales_master.utils.random_code_gen import (
    generate_random_no,
    generate_random_sc,
)
from shared.base_models import BaseMaster


class IcwSupplierCreation(BaseMaster):
    class PartyType(models.TextChoices):
        CREDITOR = "creditor", "Creditor"
        DEBITOR = "debitor", "Debitor"

    class PaymentType(models.TextChoices):
        CREDIT = "credit", "Credit"
        DEBIT = "debit", "Debit"

    supplier_date = models.DateField()
    party_type = models.CharField(max_length=10, choices=PartyType.choices)
    supplier_id = models.PositiveIntegerField(unique=True, blank=True, null=True)
    supplier_name = models.CharField(max_length=150)
    contact_person = models.CharField(max_length=150)

    country_id = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        related_name="icw_suppliers",
        to_field="unique_id",
        db_column="country_id",
    )
    state_id = models.ForeignKey(
        State,
        on_delete=models.PROTECT,
        related_name="icw_suppliers",
        to_field="unique_id",
        db_column="state_id",
    )
    district_id = models.ForeignKey(
        District,
        on_delete=models.PROTECT,
        related_name="icw_suppliers",
        to_field="unique_id",
        db_column="district_id",
    )
    city_id = models.ForeignKey(
        City,
        on_delete=models.PROTECT,
        related_name="icw_suppliers",
        to_field="unique_id",
        db_column="city_id",
    )

    phone_no = models.CharField(max_length=20, blank=True, null=True)
    mobile_no = models.CharField(max_length=20)
    other_mobile_1 = models.CharField(max_length=20, blank=True, null=True)
    other_mobile_2 = models.CharField(max_length=20, blank=True, null=True)
    other_mobile_3 = models.CharField(max_length=20, blank=True, null=True)
    whatsapp_no = models.CharField(max_length=20, blank=True, null=True)

    building_no = models.CharField(max_length=50)
    street = models.CharField(max_length=150)
    area = models.CharField(max_length=150)
    pincode = models.CharField(max_length=10)
    latitude = models.CharField(max_length=30)
    longitude = models.CharField(max_length=30)
    address = models.TextField(blank=True, null=True)

    has_gst = models.BooleanField(default=False)
    gst_no = models.CharField(max_length=20, blank=True, null=True)

    to_email = models.EmailField(blank=True, null=True)
    cc_mail = models.CharField(max_length=255, blank=True, null=True)
    quality_to_email = models.EmailField(blank=True, null=True)
    quality_cc_mail = models.CharField(max_length=255, blank=True, null=True)

    opening_balance = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0"))
    payment_type = models.CharField(max_length=10, choices=PaymentType.choices)
    sites = models.ManyToManyField(
        Site,
        related_name="icw_suppliers",
        blank=True,
    )
    item_name = models.CharField(max_length=150)
    executive = models.CharField(max_length=150)
    ac_group = models.CharField(max_length=150, blank=True, null=True)

    bank_name = models.CharField(max_length=150, blank=True, null=True)
    branch = models.CharField(max_length=150, blank=True, null=True)
    account_no = models.CharField(max_length=50, blank=True, null=True)
    ifsc_code = models.CharField(max_length=20, blank=True, null=True)
    pan_no = models.CharField(max_length=20, blank=True, null=True)

    random_no = models.CharField(max_length=5, unique=True, blank=True)
    random_sc = models.CharField(max_length=12, unique=True, blank=True)

    class Meta:
        db_table = "icw_supplier_creation"
        ordering = ["-created_at"]

    def __str__(self):
        return self.supplier_name

    def save(self, *args, **kwargs):
        if not self.supplier_id:
            last_supplier_id = (
                IcwSupplierCreation.objects.exclude(supplier_id__isnull=True)
                .order_by("-supplier_id")
                .values_list("supplier_id", flat=True)
                .first()
            )
            self.supplier_id = (last_supplier_id or 0) + 1
        if not self.random_no:
            self.random_no = generate_random_no(IcwSupplierCreation)
        if not self.random_sc:
            self.random_sc = generate_random_sc(IcwSupplierCreation)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.is_active = False
        self.save(update_fields=["is_deleted", "is_active"])
