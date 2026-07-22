from rest_framework import serializers

from apps.common_master.models.city import City
from apps.common_master.models.country import Country
from apps.common_master.models.district import District
from apps.common_master.models.site import Site
from apps.common_master.models.state import State
from apps.common_master.validators.unique_name_validator import unique_name_validator
from apps.sales_master.models.customer_creation_master import CustomerCreationMaster
from apps.sales_master.models.item_creation import ItemCreation
from apps.sales_master.serializers.customer_destination_serializer import (
    CustomerDestinationSerializer,
)
from apps.sales_master.serializers.customer_item_purpose_serializer import (
    CustomerItemPurposeSerializer,
)


class CustomerCreationMasterSerializer(serializers.ModelSerializer):

    country_id = serializers.SlugRelatedField(
        slug_field="unique_id",
        queryset=Country.objects.filter(is_deleted=False),
        error_messages={"does_not_exist": "Invalid country_id."},
    )
    state_id = serializers.SlugRelatedField(
        slug_field="unique_id",
        queryset=State.objects.filter(is_deleted=False),
        error_messages={"does_not_exist": "Invalid state_id."},
    )
    district_id = serializers.SlugRelatedField(
        slug_field="unique_id",
        queryset=District.objects.filter(is_deleted=False),
        error_messages={"does_not_exist": "Invalid district_id."},
    )
    city_id = serializers.SlugRelatedField(
        slug_field="unique_id",
        queryset=City.objects.filter(is_deleted=False),
        error_messages={"does_not_exist": "Invalid city_id."},
    )

    sites = serializers.SlugRelatedField(
        slug_field="unique_id",
        queryset=Site.objects.filter(is_deleted=False),
        many=True,
        required=False,
    )

    items = serializers.SlugRelatedField(
        slug_field="unique_id",
        queryset=ItemCreation.objects.filter(is_deleted=False),
        many=True,
        required=False,
    )

    country_name = serializers.CharField(source="country_id.name", read_only=True)
    state_name = serializers.CharField(source="state_id.name", read_only=True)
    district_name = serializers.CharField(source="district_id.name", read_only=True)
    city_name = serializers.CharField(source="city_id.name", read_only=True)
    site_names = serializers.SerializerMethodField()
    item_names = serializers.SerializerMethodField()

    customer_status = serializers.SerializerMethodField()

    destinations = CustomerDestinationSerializer(many=True, read_only=True)
    item_purposes = CustomerItemPurposeSerializer(many=True, read_only=True)

    class Meta:
        model = CustomerCreationMaster
        fields = "__all__"
        read_only_fields = (
            "unique_id",
            "address",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "country_name",
            "state_name",
            "district_name",
            "city_name",
            "site_names",
            "item_names",
            "customer_status",
            "destinations",
            "item_purposes",
        )
        validators = []

    def get_site_names(self, obj):
        return [site.site_name for site in obj.sites.all()]

    def get_item_names(self, obj):
        return [item.item_name for item in obj.items.all()]

    def get_customer_status(self, obj):
        # NOC not uploaded -> auto-approved (tick); NOC uploaded -> pending review ("P")
        return "pending" if obj.noc_upload else "approved"

    def validate(self, attrs):
        has_gst = attrs.get("has_gst", getattr(self.instance, "has_gst", False))
        gst_no = attrs.get("gst_no", getattr(self.instance, "gst_no", None))
        if has_gst and not gst_no:
            raise serializers.ValidationError(
                {"gst_no": "GST number is required when GST is Yes."}
            )

        return unique_name_validator(
            Model=CustomerCreationMaster,
            name_field="customer_name",
            scope_fields=[],
        )(self, attrs)

    def create(self, validated_data):
        sites = validated_data.pop("sites", [])
        items = validated_data.pop("items", [])
        validated_data.setdefault("is_active", True)
        instance = CustomerCreationMaster.objects.create(**validated_data)
        if sites:
            instance.sites.set(sites)
        if items:
            instance.items.set(items)
        return instance

    def update(self, instance, validated_data):
        sites = validated_data.pop("sites", None)
        items = validated_data.pop("items", None)
        instance = super().update(instance, validated_data)
        if sites is not None:
            instance.sites.set(sites)
        if items is not None:
            instance.items.set(items)
        return instance
