
from django.db import models
from django.core.exceptions import ValidationError

from shared.base_models import BaseMaster

from .vehicle_request import VehicleRequest
from .equipment_modelmaster import EquipmentModelMaster

class VehicleRequestItem(BaseMaster):

    vehicle_request = models.ForeignKey(
        VehicleRequest,
        on_delete=models.CASCADE,
        related_name="items",
    )

    equipment_model = models.ForeignKey(
        EquipmentModelMaster,
        on_delete=models.PROTECT,
        related_name="vehicle_request_items",
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

    def __str__(self):
        return f"{self.vehicle_request.request_no} - {self.equipment_model}"
