from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Q

from shared.base_models import BaseMaster
from apps.em_master.models.utils.comfun import generate_unique_id


class GstType(models.TextChoices):
    YES = "yes", "Yes"
    NO = "no", "No"


class ContractorMaster(BaseMaster):

    contractor_code = models.CharField(
        max_length=20,
        editable=False
    )

    contractor_name = models.CharField(max_length=100)
    contact_person = models.CharField(max_length=100)

    mobile_no = models.CharField(max_length=10)
    phone_no = models.CharField(max_length=10, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    gst_type = models.CharField(
        max_length=3,
        choices=GstType.choices,
        default=GstType.NO
    )
    gst_no = models.CharField(max_length=15, blank=True, null=True)

    pan_no = models.CharField(max_length=10, blank=True, null=True)

    opening_balance = models.DecimalField(max_digits=15, decimal_places=2)

    address = models.TextField()
    bank_details = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["contractor_name"]
        constraints = [
            models.UniqueConstraint(
                fields=["contractor_code"],
                condition=Q(is_deleted=False),
                name="uq_contractor_code_active"
            ),
            models.UniqueConstraint(
                fields=["mobile_no"],
                condition=Q(is_deleted=False),
                name="uq_contractor_mobile_active"
            ),
            models.UniqueConstraint(
                fields=["phone_no"],
                condition=Q(is_deleted=False) & Q(phone_no__isnull=False),
                name="uq_contractor_phone_active"
            ),
            models.UniqueConstraint(
                fields=["email"],
                condition=Q(is_deleted=False) & Q(email__isnull=False),
                name="uq_contractor_email_active"
            ),
        ]

    def __str__(self):
        return self.contractor_name

    def clean(self):
        """
        GST No is mandatory only if gst_type = YES
        """
        if self.gst_type == GstType.YES and not self.gst_no:
            raise ValidationError(
                {"gst_no": "GST number is required when GST type is Yes."}
            )

        if self.gst_type == GstType.NO:
            self.gst_no = None

    def save(self, *args, **kwargs):
        if not self.contractor_code:
            year = timezone.now().year
            self.contractor_code = f"EM-{year}-{generate_unique_id()[:4].upper()}"

        self.full_clean()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Soft delete
        """
        self.is_deleted = True
        self.is_active = False
        self.save(update_fields=["is_deleted", "is_active"])
