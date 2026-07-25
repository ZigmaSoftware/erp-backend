from django.db import models
from django.db.models import Q

from shared.base_models import BaseMaster


class ItemMinMaxTypeMaster(BaseMaster):

    type_name = models.CharField(max_length=100)
    type_description = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        ordering = ["type_name"]
        constraints = [
            models.UniqueConstraint(
                fields=["type_name"],
                condition=Q(is_deleted=False),
                name="uq_type_name_active"
            ),
        ]

    def __str__(self):
        return self.type_name

    def delete(self, *args, **kwargs):
        """
        Soft delete
        """
        self.is_deleted = True
        self.is_active = False
        self.save(update_fields=["is_deleted", "is_active"])
