from django.db import models

from shared.base_models import BaseMaster
from apps.em_master.models.utils.comfun import generate_unique_id

from apps.em_master.models.equipment_typemaster import EquipmentTypeMaster

class EquipmentModelMaster(BaseMaster):

    equipment_type = models.ForeignKey(
        EquipmentTypeMaster,
        on_delete=models.PROTECT,
        related_name="models",
        to_field="unique_id"
    )

    manufacturer = models.CharField(max_length=300)
    model_name = models.CharField(max_length=50)
    description = models.CharField(max_length=100)

    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["model_name"]

    def __str__(self):
        return self.model_name

    def save(self, *args, **kwargs):
        if not self.unique_id:
            self.unique_id = generate_unique_id()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.is_active = False
        self.save(update_fields=["is_deleted", "is_active"])
