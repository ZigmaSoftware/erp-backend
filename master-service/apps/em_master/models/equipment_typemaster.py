from django.db import models

from shared.base_models import BaseMaster
from apps.em_master.models.utils.comfun import generate_unique_id

class Category(models.TextChoices):
    MACHINERY = "machinery", "Machinery"
    TIPPER = "tipper", "Tipper"
    GENSET = "genset", "Genset"
    OTHERS = "others", "Others"


def equipmentmastertype_upload_path(instance, filename):
    return f"uploads/equipmentmastertype/{instance.unique_id}_{filename}"


class EquipmentTypeMaster(BaseMaster):

    name = models.CharField(max_length=100)
    description = models.CharField(max_length=300)
    
    category = models.CharField(
        max_length=20,
        choices=Category.choices
    )
    image = models.FileField(upload_to=equipmentmastertype_upload_path, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # Auto-assign a unique_id if missing (aligns with common master behavior)
        if not self.unique_id:
            self.unique_id = generate_unique_id()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.is_active = False
        self.save(update_fields=["is_deleted", "is_active"])
