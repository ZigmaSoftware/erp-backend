from django.db import models, transaction
from django.core.exceptions import ValidationError
from django.utils import timezone

from shared.base_models import BaseMaster
from auth_service.apps.authentication.models.user_profile import UserProfile
from ...common_master.models.site import Site
from ..utils.request_id_gen import generate_vehicle_request_no


class RequestStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    SUBMITTED = "submitted", "Submitted"
    APPROVED = "approved", "Approved"


class VehicleRequest(BaseMaster):

    request_no = models.CharField(max_length=100, unique=True, blank=True)

    request_date = models.DateField(auto_now_add=True)

    description = models.CharField(max_length=300, blank=True, null=True)

    site_id = models.ForeignKey(
        Site,
        on_delete=models.PROTECT,
        related_name="vehicle_requests",
        to_field="unique_id",
        db_column="site_id",
    )

    request_status = models.CharField(
        max_length=20,
        choices=RequestStatus.choices,
        default=RequestStatus.DRAFT,
    )

    approved_by = models.ForeignKey(
        UserProfile,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="approved_vehicle_requests",
        db_column="approved_by",
    )

    approved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.request_no or "New Request"

    def clean(self):
        # Cannot submit without at least 1 item
        if self.request_status == RequestStatus.SUBMITTED:
            if not self.pk:
                raise ValidationError("Save request before submitting.")
            if not self.items.exists():
                raise ValidationError("Cannot submit request without at least one item.")

    @transaction.atomic
    def save(self, *args, **kwargs):

        # Lock record during update
        if self.pk:
            old = VehicleRequest.objects.select_for_update().get(pk=self.pk)

            # Prevent editing after approval
            if old.request_status == RequestStatus.APPROVED:
                raise ValidationError("Approved requests cannot be modified.")

        # Auto-generate request number
        if not self.request_no:
            self.request_no = generate_vehicle_request_no(VehicleRequest)

        # Auto-fill approval timestamp
        if self.request_status == RequestStatus.APPROVED and not self.approved_at:
            self.approved_at = timezone.now()

        self.full_clean()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Soft delete
        """
        self.is_deleted = True
        self.is_active = False
        self.save(update_fields=["is_deleted", "is_active"])
