from django.db import models
from django.core.exceptions import ValidationError

from shared.base_models import BaseMaster
from .vehicle_request import VehicleRequest
from .equipment_modelmaster import EquipmentModelMaster
from .equipment_typemaster import EquipmentTypeMaster


class VehicleRequestItem(BaseMaster):

    vehicle_request_id = models.ForeignKey(
        VehicleRequest,
        on_delete=models.CASCADE,
        related_name="items",
        to_field="unique_id",
        db_column="vehicle_request_id",
    )

    equipment_type_id = models.ForeignKey(
        EquipmentTypeMaster,
        on_delete=models.PROTECT,
        related_name="vehicle_request_items",
        to_field="unique_id",
        db_column="equipment_type_id",
        
    )

    equipment_model_id = models.ForeignKey(
        EquipmentModelMaster,
        on_delete=models.PROTECT,
        related_name="vehicle_request_items",       
        to_field="unique_id",
        db_column="equipment_model_id",
        
    )

    qty = models.PositiveIntegerField()

    UNIT_CHOICES = (
        ("nos", "Nos"),
        ("hrs", "Hours"),
        ("days", "Days"),
    )

    unit = models.CharField(max_length=20, choices=UNIT_CHOICES)

    purpose = models.CharField(max_length=300, blank=True, null=True)

    class Meta:
        ordering = ["created_at"]

    def clean(self):

        #  Prevent adding items to approved request
        if self.vehicle_request.request_status == "approved":
            raise ValidationError("Cannot modify items of an approved request.")

        # Equipment Model must belong to selected Equipment Type
        if self.equipment_model.equipment_type != self.equipment_type:
            raise ValidationError(
                "Selected equipment model does not belong to selected equipment type."
            )

    def __str__(self):
        return f"{self.vehicle_request.request_no} - {self.equipment_model}"