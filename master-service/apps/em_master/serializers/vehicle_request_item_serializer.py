from django.db import transaction
from rest_framework import serializers

from apps.common_master.serializers.site import SiteSerializer
from apps.em_master.models.vehicle_request import VehicleRequest, RequestStatus
from apps.em_master.utils.request_id_gen import generate_vehicle_request_no
from apps.em_master.models.vehicle_request_item import VehicleRequestItem
from apps.em_master.models.equipment_modelmaster import EquipmentModelMaster
from auth_service.apps.authentication.models.user_profile import UserProfile
from django.contrib.auth.models import User


class UniqueIDForeignKeyField(serializers.CharField):
    def __init__(self, queryset, **kwargs):
        self.queryset = queryset
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        value = super().to_internal_value(data)
        try:
            return self.queryset.get(unique_id=value, is_deleted=False)
        except self.queryset.model.DoesNotExist:
            raise serializers.ValidationError(
                f"{self.queryset.model.__name__} with unique_id `{value}` not found."
            )

    def to_representation(self, value):
        if hasattr(value, "unique_id"):
            return str(value.unique_id)
        return super().to_representation(value)


class VehicleRequestItemBaseSerializer(serializers.ModelSerializer):
    equipment_model_id = UniqueIDForeignKeyField(
        queryset=EquipmentModelMaster.objects.filter(is_deleted=False),
    )
    equipment_type_id = serializers.CharField(
        source="equipment_type.unique_id",
        read_only=True,
    )

    class Meta:
        model = VehicleRequestItem
        fields = [
            "id",
            "unique_id",
            "equipment_model_id",
            "equipment_type_id",
            "qty",
            "unit",
            "purpose",
        ]
        read_only_fields = ["id", "unique_id", "equipment_type_id"]

    def _ensure_equipment_type(self, validated_data):
        equipment_model = validated_data.get("equipment_model_id")
        if equipment_model:
            validated_data["equipment_type_id"] = equipment_model.equipment_type
        return validated_data

    def create(self, validated_data):
        validated_data = self._ensure_equipment_type(validated_data)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        validated_data = self._ensure_equipment_type(validated_data)
        return super().update(instance, validated_data)


class VehicleRequestItemNestedSerializer(VehicleRequestItemBaseSerializer):
    class Meta(VehicleRequestItemBaseSerializer.Meta):
        pass


class VehicleRequestItemSerializer(VehicleRequestItemBaseSerializer):
    vehicle_request_id = UniqueIDForeignKeyField(
        queryset=VehicleRequest.objects.filter(is_deleted=False),
    )

    class Meta(VehicleRequestItemBaseSerializer.Meta):
        fields = VehicleRequestItemBaseSerializer.Meta.fields + ["vehicle_request_id"]
        read_only_fields = VehicleRequestItemBaseSerializer.Meta.read_only_fields


class VehicleRequestSerializer(serializers.ModelSerializer):
    items = VehicleRequestItemNestedSerializer(many=True)
    request_no = serializers.CharField(read_only=True)

    class Meta:
        model = VehicleRequest
        fields = [
            "id",
            "unique_id",
            "request_no",
            "request_date",
            "description",
            "site_id",
            "request_status",
            "items",
        ]
        read_only_fields = ["id", "unique_id", "request_no", "request_date"]

    def validate(self, attrs):
        status = attrs.get("request_status")

        if status == RequestStatus.SUBMITTED:
            items = self.initial_data.get("items", [])
            if not items:
                raise serializers.ValidationError(
                    "Cannot submit without at least one item."
                )

        return attrs

    def _prepare_item_kwargs(self, vehicle_request, item_data):
        equipment_model = item_data.get("equipment_model_id")
        if not equipment_model:
            raise serializers.ValidationError(
                "Each item must reference an equipment model."
            )

        item_kwargs = item_data.copy()
        item_kwargs["equipment_type_id"] = equipment_model.equipment_type
        item_kwargs["vehicle_request_id"] = vehicle_request
        return item_kwargs

    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop("items")

        validated_data["request_no"] = generate_vehicle_request_no(VehicleRequest)
        vehicle_request = VehicleRequest.objects.create(**validated_data)

        for item in items_data:
            VehicleRequestItem.objects.create(
                **self._prepare_item_kwargs(vehicle_request, item)
            )

        return vehicle_request

    @transaction.atomic
    def update(self, instance, validated_data):
        if instance.request_status == RequestStatus.APPROVED:
            raise serializers.ValidationError(
                "Approved request cannot be modified."
            )

        items_data = validated_data.pop("items", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        if items_data is not None:
            instance.items.all().delete()
            for item in items_data:
                VehicleRequestItem.objects.create(
                    **self._prepare_item_kwargs(instance, item)
                )

        return instance


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email"]


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = ["id", "employee_id", "phone", "user"]
        read_only_fields = fields


class VehicleRequestReadSerializer(serializers.ModelSerializer):
    items = VehicleRequestItemNestedSerializer(many=True, read_only=True)
    approved_by = UserProfileSerializer(allow_null=True, required=False)
    site = SiteSerializer(source="site_id", read_only=True)

    class Meta:
        model = VehicleRequest
        fields = [
            "id",
            "unique_id",
            "request_no",
            "request_date",
            "description",
            "site_id",
            "site",
            "request_status",
            "items",
            "approved_by",
            "approved_at",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        ]
        read_only_fields = fields
