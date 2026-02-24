from rest_framework import serializers

from apps.common_master.models.site import Site
from apps.em_master.models.contractormaster import ContractorMaster
from apps.em_master.models.equipment_modelmaster import EquipmentModelMaster
from apps.em_master.models.equipment_typemaster import EquipmentTypeMaster
from apps.em_master.models.vehicle_creation import VehicleCreation
from apps.em_master.models.vehicle_request import RequestStatus, VehicleRequest
from apps.em_master.models.vehicle_suppliermaster import VehicleSupplierMaster


class VehicleCreationSerializer(serializers.ModelSerializer):

    # -----------------------------------------
    # ForeignKey Fields (accept unique_id)
    # -----------------------------------------

    contractor_id = serializers.SlugRelatedField(
        slug_field="unique_id",
        queryset=ContractorMaster.objects.filter(is_deleted=False),
        required=False,
        allow_null=True,
        error_messages={"does_not_exist": "Invalid contractor_id."},
    )

    supplier_id = serializers.SlugRelatedField(
        slug_field="unique_id",
        queryset=VehicleSupplierMaster.objects.filter(is_deleted=False),
        required=False,
        allow_null=True,
        error_messages={"does_not_exist": "Invalid supplier_id."},
    )

    request_id = serializers.SlugRelatedField(
        slug_field="unique_id",
        queryset=VehicleRequest.objects.filter(is_deleted=False),
        error_messages={"does_not_exist": "Invalid request_id."},
    )

    site_id = serializers.SlugRelatedField(
        slug_field="unique_id",
        queryset=Site.objects.filter(is_deleted=False),
        error_messages={"does_not_exist": "Invalid site_id."},
    )

    equipment_type_id = serializers.SlugRelatedField(
        slug_field="unique_id",
        queryset=EquipmentTypeMaster.objects.filter(is_deleted=False),
        error_messages={"does_not_exist": "Invalid equipment_type_id."},
    )

    equipment_model_id = serializers.SlugRelatedField(
        slug_field="unique_id",
        queryset=EquipmentModelMaster.objects.filter(is_deleted=False),
        error_messages={"does_not_exist": "Invalid equipment_model_id."},
    )

    # -----------------------------------------
    # Name Fields (GET only)
    # -----------------------------------------

    contractor_name = serializers.CharField(
        source="contractor_id.contractor_name",
        read_only=True,
    )

    supplier_name = serializers.CharField(
        source="supplier_id.supplier_name",
        read_only=True,
    )

    request_no = serializers.CharField(
        source="request_id.request_no",
        read_only=True,
    )

    site_name = serializers.CharField(
        source="site_id.site_name",
        read_only=True,
    )

    equipment_type_name = serializers.CharField(
        source="equipment_type_id.name",
        read_only=True,
    )

    equipment_model_name = serializers.CharField(
        source="equipment_model_id.model_name",
        read_only=True,
    )

    # -----------------------------------------

    class Meta:
        model = VehicleCreation
        fields = "__all__"

        read_only_fields = [
            "unique_id",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "contractor_name",
            "supplier_name",
            "request_no",
            "site_name",
            "equipment_type_name",
            "equipment_model_name",
        ]

        validators = []

    # -----------------------------------------
    # Business Validation Only
    # -----------------------------------------

    def validate(self, attrs):

        site = attrs.get("site_id", getattr(self.instance, "site_id", None))
        vehicle = attrs.get("vehicle_id", getattr(self.instance, "vehicle_id", None))
        equipment_model = attrs.get("equipment_model_id", getattr(self.instance, "equipment_model_id", None))
        equipment_type = attrs.get("equipment_type_id", getattr(self.instance, "equipment_type_id", None))

        errors = {}

        if vehicle and not vehicle.is_active:
            errors["vehicle_id"] = "Selected vehicle is inactive."

        if vehicle and site:
            if vehicle.site_id != site:
                errors["site_id"] = "Selected site must match vehicle's site."

        if equipment_model and equipment_type:
            if equipment_model.equipment_type_id != equipment_type:
                errors["equipment_model_id"] = (
                    "Selected equipment model does not belong to chosen type."
                )

        if errors:
            raise serializers.ValidationError(errors)

        return attrs