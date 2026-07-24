from django.db import models
from django.db.models import Q

from shared.base_models import BaseMaster

from apps.common_master.models.country import Country
from apps.common_master.models.state import State
from apps.common_master.models.district import District
from apps.common_master.models.city import City
from apps.common_master.models.site import Site
from apps.sales_master.models.item_creation import ItemCreation


class CustomerCreationMaster(BaseMaster):

    class CustomerType(models.TextChoices):
        CREDITOR = "creditor", "Creditor"
        DEBITOR = "debitor", "Debitor"

    class PaymentType(models.TextChoices):
        CREDIT = "credit", "Credit"
        DEBIT = "debit", "Debit"

    # -------------------------
    # Customer Details
    # -------------------------
    entry_date = models.DateField()
    customer_type = models.CharField(max_length=10, choices=CustomerType.choices)
    customer_name = models.CharField(max_length=150)
    contact_person = models.CharField(max_length=150)

    phone_no = models.CharField(max_length=20, blank=True, null=True)
    mobile_code = models.CharField(max_length=10, blank=True, null=True)
    mobile_no = models.CharField(max_length=20)
    other_mobile_1 = models.CharField(max_length=20, blank=True, null=True)
    other_mobile_2 = models.CharField(max_length=20, blank=True, null=True)
    other_mobile_3 = models.CharField(max_length=20, blank=True, null=True)
    whatsapp_no = models.CharField(max_length=20, blank=True, null=True)

    country_id = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        related_name="customers",
        to_field="unique_id",
        db_column="country_id",
    )
    state_id = models.ForeignKey(
        State,
        on_delete=models.PROTECT,
        related_name="customers",
        to_field="unique_id",
        db_column="state_id",
    )
    district_id = models.ForeignKey(
        District,
        on_delete=models.PROTECT,
        related_name="customers",
        to_field="unique_id",
        db_column="district_id",
    )
    city_id = models.ForeignKey(
        City,
        on_delete=models.PROTECT,
        related_name="customers",
        to_field="unique_id",
        db_column="city_id",
    )

    building_no = models.CharField(max_length=50)
    street = models.CharField(max_length=150)
    area = models.CharField(max_length=150)
    pincode = models.CharField(max_length=10)
    address = models.CharField(max_length=250, blank=True)

    lat = models.CharField(max_length=50)
    lon = models.CharField(max_length=50)

    has_gst = models.BooleanField(default=False)
    gst_no = models.CharField(max_length=20, blank=True, null=True)

    to_email = models.EmailField(blank=True, null=True)
    cc_mail = models.CharField(max_length=255, blank=True, null=True)
    quality_email_id = models.EmailField(blank=True, null=True)
    quality_cc_mail = models.CharField(max_length=255, blank=True, null=True)

    opening_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    payment_type = models.CharField(max_length=10, choices=PaymentType.choices)

    sites = models.ManyToManyField(Site, related_name="customers", blank=True)
    items = models.ManyToManyField(ItemCreation, related_name="customers", blank=True)
    executive_name = models.CharField(max_length=150, blank=True, null=True)
    acc_group = models.CharField(max_length=150, blank=True, null=True)

    noc_upload = models.BooleanField(default=False)

    # -------------------------
    # Bank Details
    # -------------------------
    bank_name = models.CharField(max_length=150, blank=True, null=True)
    branch = models.CharField(max_length=150, blank=True, null=True)
    account_no = models.CharField(max_length=50, blank=True, null=True)
    ifsc_code = models.CharField(max_length=20, blank=True, null=True)
    pan_no = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["customer_name"],
                condition=Q(is_deleted=False),
                name="uq_customer_name_active",
            ),
        ]

    def __str__(self):
        return self.customer_name

    def save(self, *args, **kwargs):
        self.address = ", ".join(
            part
            for part in [self.building_no, self.street, self.area, self.pincode]
            if part
        )
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Soft delete (cascades to destinations and item/purpose rows)
        """
        self.is_deleted = True
        self.is_active = False
        self.save(update_fields=["is_deleted", "is_active"])
        self.destinations.filter(is_deleted=False).update(
            is_deleted=True, is_active=False
        )
        self.item_purposes.filter(is_deleted=False).update(
            is_deleted=True, is_active=False
        )
