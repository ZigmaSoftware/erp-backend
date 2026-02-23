from rest_framework import serializers

from apps.common_master.models.site import Site
from apps.em_master.models.contractormaster import ContractorMaster
from apps.em_master.models.equipment_modelmaster import EquipmentModelMaster
from apps.em_master.models.equipment_typemaster import EquipmentTypeMaster
from apps.em_master.models.vehicle_creation import VehicleCreation
from apps.em_master.models.vehicle_request import RequestStatus, VehicleRequest
from apps.em_master.models.vehicle_suppliermaster import VehicleSupplierMaster


class VehicleCreationSerializer(serializers.ModelSerializer):
    contractor = serializers.SlugRelatedField(
        slug_field="unique_id",
        queryset=ContractorMaster.objects.filter(is_deleted=False),
        allow_null=True,
        required=False,
    )

    supplier = serializers.SlugRelatedField(
        slug_field="unique_id",
        queryset=VehicleSupplierMaster.objects.filter(is_deleted=False),
        allow_null=True,
        required=False,
    )

    request = serializers.SlugRelatedField(
        slug_field="unique_id",
        queryset=VehicleRequest.objects.filter(is_deleted=False),
    )

    site = serializers.SlugRelatedField(
        slug_field="unique_id",
        queryset=Site.objects.filter(is_deleted=False),
    )

    equipment_type = serializers.SlugRelatedField(
        slug_field="unique_id",
        queryset=EquipmentTypeMaster.objects.filter(is_deleted=False),
    )

    equipment_model = serializers.SlugRelatedField(
        slug_field="unique_id",
        queryset=EquipmentModelMaster.objects.filter(is_deleted=False),
    )

    class Meta:
        model = VehicleCreation
        fields = [
            "id",
            "unique_id",
            "vehicle_code",
            "hire_type",
            "contractor",
            "supplier",
            "request",
            "site",
            "equipment_type",
            "equipment_model",
            "vehicle_reg_no",
            "permit_expiry",
            "fc_expiry",
            "insurance_expiry",
            "road_tax_expiry",
            "rental_basis",
            "target_hours",
            "plant_entry_date",
            "rc_invoice_date",
            "is_active",
            "is_deleted",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        ]

        read_only_fields = [
            "id",
            "unique_id",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        ]

    def validate(self, attrs):
        """
        Business Rules:
        1. Request must exist and be APPROVED
        2. If hire_type = HIRE → contractor or supplier required
        3. If hire_type = OWN → contractor and supplier must be empty
        4. Contractor and supplier cannot both be provided
        """

        hire_type = attrs.get(
            "hire_type",
            getattr(self.instance, "hire_type", None),
        )

        contractor = attrs.get(
            "contractor",
            getattr(self.instance, "contractor", None),
        )

        supplier = attrs.get(
            "supplier",
            getattr(self.instance, "supplier", None),
        )

        request = attrs.get(
            "request",
            getattr(self.instance, "request", None),
        )

        # --- Request validation ---
        if not request:
            raise serializers.ValidationError(
                {"request": "Request is required."}
            )

        if request.request_status != RequestStatus.APPROVED:
            raise serializers.ValidationError(
                {"request": "Vehicle can only be created for APPROVED requests."}
            )

        # --- Hire type validation ---
        if hire_type == VehicleCreation.HireType.HIRE:
            if not contractor and not supplier:
                raise serializers.ValidationError(
                    {
                        "contractor": "Contractor or Supplier is required when hire type is HIRE."
                    }
                )

        if hire_type == VehicleCreation.HireType.OWN:
            if contractor or supplier:
                raise serializers.ValidationError(
                    {
                        "hire_type": "Contractor and Supplier must be empty when hire type is OWN."
                    }
                )

        # --- Mutual exclusivity (optional but recommended) ---
        if contractor and supplier:
            raise serializers.ValidationError(
                {
                    "supplier": "Only one of contractor or supplier can be provided."
                }
            )

        return attrs