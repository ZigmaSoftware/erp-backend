from django.db import models
from django.db.models import Q

from shared.base_models import BaseMaster


class RemarkSiteStoreCreationMaster(BaseMaster):

    remark_type = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["remark_type"]
        constraints = [
            models.UniqueConstraint(
                fields=["remark_type"],
                condition=Q(is_deleted=False),
                name="uq_remark_type_active"
            ),
        ]

    def __str__(self):
        return self.remark_type

    def delete(self, *args, **kwargs):
        """
        Soft delete
        """
        self.is_deleted = True
        self.is_active = False
        self.save(update_fields=["is_deleted", "is_active"])
