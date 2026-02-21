from django.db import models

from shared.base_models import BaseMaster
from apps.em_master.models.equipment_typemaster import EquipmentTypeMaster


class EquipmentModelMaster(BaseMaster):

    equipment_type = models.ForeignKey(
        EquipmentTypeMaster,
        on_delete=models.PROTECT,
        related_name="models",
        to_field="unique_id",
        db_column="equipment_type_id",
    )

    manufacturer = models.CharField(max_length=300)
    model_name = models.CharField(max_length=50)
    description = models.CharField(max_length=100)

    class Meta:
        ordering = ["model_name"]

    def __str__(self):
        return self.model_name

    def delete(self, *args, **kwargs):
        """
        Soft delete
        """
        self.is_deleted = True
        self.is_active = False
        self.save(update_fields=["is_deleted", "is_active"])
