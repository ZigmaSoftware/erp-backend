from decimal import Decimal

from django.db import models
from django.db.models import Q

from shared.base_models import BaseMaster


class SupplierCreationMaster(BaseMaster):

    class PartyType(models.TextChoices):
        CREDITOR = "creditor", "Creditor"
        DEBITOR = "debitor", "Debitor"

    class PaymentType(models.TextChoices):
        CREDIT = "credit", "Credit"
        DEBIT = "debit", "Debit"

    class SupplierCategory(models.IntegerChoices):
        DEALER = 1, "Dealer"
        DISTRIBUTOR = 2, "Distributor"
        MANUFACTURER = 3, "Manufacturer"
        SERVICE_PROVIDER = 4, "Service Provider"

    supplier_code = models.CharField(max_length=20, unique=True, editable=False)

    party_type = models.CharField(max_length=10, choices=PartyType.choices)
    party_name = models.CharField(max_length=100)
    proprietor_name = models.CharField(max_length=50, blank=True, null=True)
    contact_person = models.CharField(max_length=100, blank=True, null=True)

    phone_no = models.CharField(max_length=20, blank=True, null=True)
    mobile_no = models.CharField(max_length=15)
    other_mobile_1 = models.CharField(max_length=20, blank=True, null=True)
    other_mobile_2 = models.CharField(max_length=20, blank=True, null=True)
    other_mobile_3 = models.CharField(max_length=20, blank=True, null=True)
    whatsapp_no = models.CharField(max_length=20, blank=True, null=True)

    # Master Service Country/State/District/City `unique_id`s (no DB-level FK -
    # cross-service reference, see stores_service/apps/stores_master/models/godown_creation_master.py
    # for the same pattern applied to Site).
    country_id = models.UUIDField()
    state_id = models.UUIDField()
    district_id = models.UUIDField()
    city_id = models.UUIDField()

    building_no = models.CharField(max_length=50)
    street = models.CharField(max_length=150)
    area = models.CharField(max_length=150)
    pincode = models.CharField(max_length=10)
    address = models.TextField(blank=True, null=True)
    latitude = models.CharField(max_length=30, blank=True, null=True)
    longitude = models.CharField(max_length=30, blank=True, null=True)

    # Plain list of Master Service Site `unique_id`s (no DB-level M2M).
    sites = models.JSONField(default=list, blank=True)

    has_gst = models.BooleanField(default=False)
    gst_no = models.CharField(max_length=20, blank=True, null=True)
    pan_no = models.CharField(max_length=10, blank=True, null=True)

    bank_name = models.CharField(max_length=150, blank=True, null=True)
    branch = models.CharField(max_length=150, blank=True, null=True)
    ac_no = models.CharField(max_length=50, blank=True, null=True)
    ifsc_code = models.CharField(max_length=20, blank=True, null=True)

    opening_balance = models.DecimalField(max_digits=15, decimal_places=2, default=Decimal("0"))
    payment_type = models.CharField(
        max_length=10, choices=PaymentType.choices, blank=True, null=True
    )
    ac_group = models.CharField(max_length=150, blank=True, null=True)

    email_id = models.EmailField(blank=True, null=True)
    cc_mail = models.CharField(max_length=255, blank=True, null=True)
    quality_mail = models.EmailField(blank=True, null=True)
    bcc_email_id = models.CharField(max_length=255, blank=True, null=True)

    supplier_category = models.PositiveSmallIntegerField(
        choices=SupplierCategory.choices, blank=True, null=True
    )
    scope_of_supply = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        ordering = ["party_name"]
        constraints = [
            models.UniqueConstraint(
                fields=["party_name", "mobile_no"],
                condition=Q(is_deleted=False),
                name="uq_supplier_party_name_mobile_active"
            ),
        ]

    def __str__(self):
        return f"{self.supplier_code} - {self.party_name}"

    def save(self, *args, **kwargs):
        if not self.supplier_code:
            last_numeric_suffix = 0
            last_code = (
                SupplierCreationMaster.objects.filter(supplier_code__startswith="SP")
                .order_by("-id")
                .values_list("supplier_code", flat=True)
                .first()
            )
            if last_code:
                try:
                    last_numeric_suffix = int(last_code[2:])
                except ValueError:
                    last_numeric_suffix = 0
            self.supplier_code = f"SP{last_numeric_suffix + 1}"
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Soft delete
        """
        self.is_deleted = True
        self.is_active = False
        self.save(update_fields=["is_deleted", "is_active"])
