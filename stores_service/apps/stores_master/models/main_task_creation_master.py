from django.db import models
from django.db.models import Q

from shared.base_models import BaseMaster


class MainTaskCreationMaster(BaseMaster):

    main_task = models.CharField(max_length=100)
    description = models.CharField(max_length=300, blank=True, null=True)

    class Meta:
        ordering = ["main_task"]
        constraints = [
            models.UniqueConstraint(
                fields=["main_task"],
                condition=Q(is_deleted=False),
                name="uq_main_task_active"
            ),
        ]

    def __str__(self):
        return self.main_task

    def delete(self, *args, **kwargs):
        """
        Soft delete
        """
        self.is_deleted = True
        self.is_active = False
        self.save(update_fields=["is_deleted", "is_active"])
