from django.db import models
from django.db.models import Q

from shared.base_models import BaseMaster


class GodownCreationMaster(BaseMaster):

    # Master Service Site `unique_id` (no DB-level FK - cross-service reference).
    site_id = models.UUIDField()

    godown_name = models.CharField(max_length=100)
    godown_address = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["godown_name"]
        constraints = [
            models.UniqueConstraint(
                fields=["site_id", "godown_name"],
                condition=Q(is_deleted=False),
                name="uq_godown_name_active_per_site"
            ),
        ]

    def __str__(self):
        return self.godown_name

    def delete(self, *args, **kwargs):
        """
        Soft delete
        """
        self.is_deleted = True
        self.is_active = False
        self.save(update_fields=["is_deleted", "is_active"])
