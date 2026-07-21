from django.db import models
from django.db.models import Q

from shared.base_models import BaseMaster


class TransportMediumCreationMaster(BaseMaster):

    vehicle_name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["vehicle_name"]
        constraints = [
            models.UniqueConstraint(
                fields=["vehicle_name"],
                condition=Q(is_deleted=False),
                name="uq_transport_medium_vehicle_name_active",
            ),
        ]

    def __str__(self):
        return self.vehicle_name

    def delete(self, *args, **kwargs):
        """
        Soft delete
        """
        self.is_deleted = True
        self.is_active = False
        self.save(update_fields=["is_deleted", "is_active"])
