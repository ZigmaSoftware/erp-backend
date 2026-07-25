from django.db import models
from django.db.models import Q

from shared.base_models import BaseMaster

from apps.stores_master.models.group_creation_master import GroupCreationMaster


class SubGroupCreationMaster(BaseMaster):

    group = models.ForeignKey(
        GroupCreationMaster,
        on_delete=models.PROTECT,
        related_name="subgroups",
        to_field="unique_id",
        db_column="group_id",
    )
    subgroup_name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["subgroup_name"]
        constraints = [
            models.UniqueConstraint(
                fields=["group", "subgroup_name"],
                condition=Q(is_deleted=False),
                name="uq_subgroup_name_active",
            ),
        ]

    def __str__(self):
        return self.subgroup_name

    def delete(self, *args, **kwargs):
        """
        Soft delete
        """
        self.is_deleted = True
        self.is_active = False
        self.save(update_fields=["is_deleted", "is_active"])
