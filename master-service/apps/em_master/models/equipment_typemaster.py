from django.db import models

from shared.base_models import BaseMaster


class Category(models.TextChoices):
    MACHINERY = "machinery", "Machinery"
    TIPPER = "tipper", "Tipper"
    GENSET = "genset", "Genset"
    OTHERS = "others", "Others"


def equipmentmastertype_upload_path(instance, filename):
    return f"equipmentmastertype/{instance.unique_id}_{filename}"


class EquipmentTypeMaster(BaseMaster):

    name = models.CharField(max_length=100)
    description = models.CharField(max_length=300)

    category = models.CharField(
        max_length=20,
        choices=Category.choices
    )

    image = models.FileField(
        upload_to=equipmentmastertype_upload_path,
        null=True,
        blank=True
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def delete(self, *args, **kwargs):
        """
        Soft delete
        """
        self.is_deleted = True
        self.is_active = False
        self.save(update_fields=["is_deleted", "is_active"])
