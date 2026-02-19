from django.db import transaction
from rest_framework import serializers

from auth_service.apps.authentication.models.user_profile import UserProfile

from apps.em_master.models.vehicle_request import VehicleRequest, RequestStatus
from apps.em_master.utils.request_id_gen import generate_vehicle_request_no


from apps.em_master.models.vehicle_request_item import VehicleRequestItem
from apps.em_master.models.equipment_modelmaster import EquipmentModelMaster


# -----------------------------
# Child Serializer
# -----------------------------
class VehicleRequestItemSerializer(serializers.ModelSerializer):
    equipment_model = serializers.SlugRelatedField(
        slug_field="unique_id",
        queryset=EquipmentModelMaster.objects.filter(is_active=True),
    )

    class Meta:
        model = VehicleRequestItem
        fields = [
            "id",
            "equipment_model",
            "qty",
            "unit",
            "purpose",
        ]


# -----------------------------
# Parent Serializer (Nested)
# -----------------------------
class VehicleRequestSerializer(serializers.ModelSerializer):
    items = VehicleRequestItemSerializer(many=True)
    staff = serializers.PrimaryKeyRelatedField(
        queryset=UserProfile.objects.filter(user__is_active=True)
    )
    request_no = serializers.CharField(read_only=True)

    class Meta:
        model = VehicleRequest
        fields = [
            "id",
            "request_no",
            "request_date",
            "description",
            "staff",
            "site",
            "request_status",
            "items",
        ]
        read_only_fields = ["request_no", "request_date"]

    # -----------------------------
    # Validation
    # -----------------------------
    def validate(self, attrs):
        status = attrs.get("request_status")

        if status == RequestStatus.SUBMITTED:
            items = self.initial_data.get("items", [])
            if not items:
                raise serializers.ValidationError(
                    "Cannot submit without at least one item."
                )

        return attrs

    # -----------------------------
    # CREATE (Atomic)
    # -----------------------------
    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop("items")

        validated_data["request_no"] = generate_vehicle_request_no(VehicleRequest)
        vehicle_request = VehicleRequest.objects.create(**validated_data)

        for item in items_data:
            VehicleRequestItem.objects.create(
                vehicle_request=vehicle_request,
                **item
            )

        return vehicle_request

    # -----------------------------
    # UPDATE (Atomic)
    # -----------------------------
    @transaction.atomic
    def update(self, instance, validated_data):

        # Lock if approved
        if instance.request_status == RequestStatus.APPROVED:
            raise serializers.ValidationError(
                "Approved request cannot be modified."
            )

        items_data = validated_data.pop("items", None)

        # Update parent fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        # Update items if provided
        if items_data is not None:
            instance.items.all().delete()

            for item in items_data:
                VehicleRequestItem.objects.create(
                    vehicle_request=instance,
                    **item
                )

        return instance
