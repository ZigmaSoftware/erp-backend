from django.db import models
from django.db.models import Q

from shared.base_models import BaseMaster


class UnitCreationMaster(BaseMaster):

    unit_name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["unit_name"]
        constraints = [
            models.UniqueConstraint(
                fields=["unit_name"],
                condition=Q(is_deleted=False),
                name="uq_unit_name_active"
            ),
        ]

    def __str__(self):
        return self.unit_name

    def delete(self, *args, **kwargs):
        """
        Soft delete
        """
        self.is_deleted = True
        self.is_active = False
        self.save(update_fields=["is_deleted", "is_active"])
