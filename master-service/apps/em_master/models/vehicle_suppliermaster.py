from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Q

from shared.base_models import BaseMaster
from apps.em_master.models.utils.comfun import generate_unique_id


class TransportType(models.TextChoices):
    MACHINERY = "machinery", "Machinery"
    TIPPER = "tipper", "Tipper"
    GENSET = "genset", "Genset"
    OTHERS = "others", "Others"


class GstType(models.TextChoices):
    YES = "yes", "Yes"
    NO = "no", "No"


def vehiclesuppliermaster_upload_path(instance, filename):
    return f"vehiclesuppliermaster/{instance.unique_id}_{filename}"


class VehicleSupplierMaster(BaseMaster):

    supplier_code = models.CharField(
        max_length=20,
        editable=False
    )

    supplier_name = models.CharField(max_length=100)
    proprietor_name = models.CharField(max_length=100)

    mobile_no = models.CharField(max_length=10)
    email = models.EmailField(blank=True, null=True)

    gst_type = models.CharField(
        max_length=3,
        choices=GstType.choices,
        default=GstType.NO
    )
    gst_no = models.CharField(max_length=15, blank=True, null=True)

    pan_no = models.CharField(max_length=10, blank=True, null=True)

    transport_medium = models.CharField(
        max_length=20, 
        choices=TransportType.choices,
        blank=True,
        null=True
    )

    address = models.TextField()
    bank_details = models.TextField(blank=True, null=True)

    image = models.FileField(
        upload_to=vehiclesuppliermaster_upload_path,
        null=True,
        blank=True
    )

    class Meta:
        ordering = ["supplier_name"]  
        constraints = [
            models.UniqueConstraint(
                fields=["supplier_code"],
                condition=Q(is_deleted=False),
                name="uq_supplier_code_active"
            ),
            models.UniqueConstraint(
                fields=["mobile_no"],
                condition=Q(is_deleted=False),
                name="uq_supplier_mobile_active"
            ),
            models.UniqueConstraint(
                fields=["email"],
                condition=Q(is_deleted=False) & Q(email__isnull=False),
                name="uq_supplier_email_active"
            ),
        ]

    def __str__(self):
        return self.supplier_name 

    def clean(self):
        if self.gst_type == GstType.YES and not self.gst_no:
            raise ValidationError(
                {"gst_no": "GST number is required when GST type is Yes."}
            )

        if self.gst_type == GstType.NO:
            self.gst_no = None

    def save(self, *args, **kwargs):
        if not self.supplier_code:  
            year = timezone.now().year
            self.supplier_code = f"EM-{year}-{generate_unique_id()[:4].upper()}"

        self.full_clean()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.is_active = False
        self.save(update_fields=["is_deleted", "is_active"])
