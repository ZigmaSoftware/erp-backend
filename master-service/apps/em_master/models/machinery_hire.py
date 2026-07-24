from django.db import models
from django.core.exceptions import ValidationError

from shared.base_models import BaseMaster

from apps.common_master.models.site import Site
from .equipment_modelmaster import EquipmentModelMaster
from .equipment_typemaster import EquipmentTypeMaster
from .vehicle_creation import VehicleCreation


class MachineryHire(BaseMaster):

    class DieselStatus(models.TextChoices):
        WITH_DIESEL = "WITH_DIESEL", "With Diesel"
        WITHOUT_DIESEL = "WITHOUT_DIESEL", "Without Diesel"

    class UnitType(models.TextChoices):
        HR = "HR", "Hour"
        M3 = "M3", "Cubic Meter"
        KM = "KM", "Kilometer"

    site_id = models.ForeignKey(
        Site,
        on_delete=models.PROTECT,
        related_name="machinery_hires",
        to_field="unique_id",
        db_column="site_id",
    )

    date = models.DateField()

    diesel_status = models.CharField(
        max_length=20,
        choices=DieselStatus.choices,
    )

    equipment_type_id = models.ForeignKey(
        EquipmentTypeMaster,
        on_delete=models.PROTECT,
        related_name="machinery_hires",
        to_field="unique_id",
        db_column="equipment_type_id",
    )

    equipment_model_id = models.ForeignKey(
        EquipmentModelMaster,
        on_delete=models.PROTECT,
        related_name="machinery_hires",
        to_field="unique_id",
        db_column="equipment_model_id",
    )

    vehicle_id = models.ForeignKey(
        VehicleCreation,
        on_delete=models.PROTECT,
        related_name="machinery_hires",
        to_field="unique_id",
        db_column="vehicle_id",
    )

    hire_rate = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    unit = models.CharField(
        max_length=5,
        choices=UnitType.choices,
    )

    def clean(self):
        """
        Business Rules:
        1. Vehicle must be active
        2. Site must match vehicle site
        """

        if self.vehicle:
            # Rule 1: Vehicle must be active
            if not self.vehicle.is_active:
                raise ValidationError("Selected vehicle is inactive.")

            # Rule 2: Site must match vehicle site
            if self.site_id != self.vehicle.site_id:
                raise ValidationError(
                    "Selected site does not match vehicle site."
                )

    def __str__(self):
        return f"{self.vehicle.vehicle_code} - {self.date}"
