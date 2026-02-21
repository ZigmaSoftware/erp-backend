import re

from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import serializers

from auth_service.apps.authentication.models.user_profile import UserProfile

from apps.common_master.serializers.site import SiteSerializer
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
class StaffRelatedField(serializers.PrimaryKeyRelatedField):
    """
    Accept either a UserProfile PK, or a remote user identifier (prefers UserProfile but will create
    a placeholder User/UserProfile when the staff id only exists on the gateway JWT).
    """

    def __init__(self, **kwargs):
        kwargs.setdefault(
            "queryset", UserProfile.objects.filter(user__is_active=True)
        )
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        try:
            return super().to_internal_value(data)
        except serializers.ValidationError:
            try:
                user = self._resolve_or_create_user(data)
            except ValueError:
                raise serializers.ValidationError("Invalid staff identifier.")

            profile, _ = UserProfile.objects.get_or_create(user=user)
            return profile

    def _resolve_or_create_user(self, identifier):
        """
        When there is no local UserProfile for the provided id, create a placeholder User so the
        request can be tied to the remote staff ID coming from the JWT/gateway.
        """

        try:
            return User.objects.get(pk=int(identifier), is_active=True)
        except (User.DoesNotExist, ValueError, TypeError):
            pass

        username = self._remote_username(identifier)

        user, created = User.objects.get_or_create(username=username)
        if created:
            user.set_unusable_password()
            user.is_active = True
            user.save(update_fields=["password", "is_active"])

        return user

    def _remote_username(self, identifier):
        """
        Build a deterministic username from the remote identifier so repeated requests map to the
        same placeholder user.
        """

        sanitized = re.sub(r"[^\w]+", "_", str(identifier or ""))
        sanitized = sanitized.strip("_")[:60] or "remote"
        return f"remote_user_{sanitized}"


class VehicleRequestSerializer(serializers.ModelSerializer):
    items = VehicleRequestItemSerializer(many=True)
    staff = StaffRelatedField()
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
    items = VehicleRequestItemSerializer(many=True, read_only=True)
    staff = UserProfileSerializer()
    approved_by = UserProfileSerializer(allow_null=True, required=False)
    site = SiteSerializer()

    class Meta:
        model = VehicleRequest
        fields = [
            "id",
            "unique_id",
            "request_no",
            "request_date",
            "description",
            "staff",
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
