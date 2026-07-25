from django.db import models
from django.db.models import Q

from shared.base_models import BaseMaster


class TaskCreationMaster(BaseMaster):

    class TaskType(models.TextChoices):
        CAPEX = "capex", "Capex"
        OPEX = "opex", "Opex"

    task_type = models.CharField(max_length=20, choices=TaskType.choices)
    task_name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["task_name"]
        constraints = [
            models.UniqueConstraint(
                fields=["task_type", "task_name"],
                condition=Q(is_deleted=False),
                name="uq_task_name_active_per_type"
            ),
        ]

    def __str__(self):
        return f"{self.task_name} ({self.get_task_type_display()})"

    def delete(self, *args, **kwargs):
        """
        Soft delete
        """
        self.is_deleted = True
        self.is_active = False
        self.save(update_fields=["is_deleted", "is_active"])
