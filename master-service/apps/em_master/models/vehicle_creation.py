from django.db import models
from django.core.exceptions import ValidationError

from shared.base_models import BaseMaster

from apps.common_master.models.site import Site

from .contractormaster import ContractorMaster
from .equipment_modelmaster import EquipmentModelMaster
from .equipment_typemaster import EquipmentTypeMaster
from .vehicle_request import RequestStatus
from .vehicle_suppliermaster import VehicleSupplierMaster
from .vehicle_request import VehicleRequest


class VehicleCreation(BaseMaster):

    class HireType(models.TextChoices):
        OWN = "OWN", "Own"
        HIRE = "HIRE", "Hire"

    class RentalBasis(models.TextChoices):
        HOUR = "HOUR", "Hour"
        DAY = "DAY", "Day"
        KM = "KM", "Km"

    vehicle_code = models.CharField(
        max_length=50,
        unique=True
    )

    hire_type = models.CharField(
        max_length=10,
        choices=HireType.choices
    )

    contractor_id = models.ForeignKey(
        ContractorMaster,
        on_delete=models.PROTECT,
        related_name="vehicles",
        to_field="unique_id",
        db_column="contractor_id",
    )

    supplier_id = models.ForeignKey(
        VehicleSupplierMaster,
        on_delete=models.PROTECT,
        related_name="vehicles",
        to_field="unique_id",
        db_column="supplier_id",
    )

    request_id = models.ForeignKey(
        VehicleRequest,
        on_delete=models.PROTECT,  # must not delete approved request
        related_name="vehicles",
        to_field="unique_id",
        db_column="request_id",
    )

    site_id = models.ForeignKey(
        Site,
        on_delete=models.PROTECT,
        related_name="vehicles",
        to_field="unique_id",
        db_column="site_id",
        
    )

    equipment_type_id = models.ForeignKey(
        EquipmentTypeMaster,
        on_delete=models.PROTECT,
        related_name="vehicles",
        to_field="unique_id",
        db_column="equipment_type_id",
    )

    equipment_model_id = models.ForeignKey(
        EquipmentModelMaster,
        on_delete=models.PROTECT,
        related_name="vehicles",
        to_field="unique_id",
        db_column="equipment_model_id",
    )

    # One vehicle = one unique registration number
    vehicle_reg_no = models.CharField(
        max_length=50,
        unique=True
    )

    # Expiry dates are mandatory
    permit_expiry = models.DateField()
    fc_expiry = models.DateField()
    insurance_expiry = models.DateField()
    road_tax_expiry = models.DateField()

    rental_basis = models.CharField(
        max_length=10,
        choices=RentalBasis.choices
    )

    target_hours = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    plant_entry_date = models.DateField(null=True, blank=True)
    rc_invoice_date = models.DateField(null=True, blank=True)

    def clean(self):
        """
        Business Validations
        """

        #  Request must be approved
        if self.request and self.request.request_status != RequestStatus.APPROVED:
            raise ValidationError("Vehicle can only be created for APPROVED requests.")

        # Hire Type Logic
        if self.hire_type == self.HireType.HIRE:
            if not self.contractor and not self.supplier:
                raise ValidationError(
                    "Contractor or Supplier is required when hire type is HIRE."
                )

        if self.hire_type == self.HireType.OWN:
            if self.contractor or self.supplier:
                raise ValidationError(
                    "Contractor and Supplier must be empty when hire type is OWN."
                )

    def __str__(self):
        return f"{self.vehicle_code} - {self.vehicle_reg_no}"
    
