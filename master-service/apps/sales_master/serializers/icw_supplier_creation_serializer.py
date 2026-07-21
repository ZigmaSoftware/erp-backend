from rest_framework import serializers

from apps.common_master.models.city import City
from apps.common_master.models.country import Country
from apps.common_master.models.district import District
from apps.common_master.models.site import Site
from apps.common_master.models.state import State
from apps.common_master.validators.unique_name_validator import unique_name_validator
from apps.sales_master.models.icw_supplier_creation import IcwSupplierCreation


class IcwSupplierCreationSerializer(serializers.ModelSerializer):
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
        error_messages={"does_not_exist": "Invalid site selection."},
    )

    country_name = serializers.CharField(source="country_id.name", read_only=True)
    state_name = serializers.CharField(source="state_id.name", read_only=True)
    district_name = serializers.CharField(source="district_id.name", read_only=True)
    city_name = serializers.CharField(source="city_id.name", read_only=True)
    site_names = serializers.SerializerMethodField()

    class Meta:
        model = IcwSupplierCreation
        fields = "__all__"
        read_only_fields = (
            "unique_id",
            "customer_id",
            "random_no",
            "random_sc",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "country_name",
            "state_name",
            "district_name",
            "city_name",
            "site_names",
        )
        validators = []

    def get_site_names(self, obj):
        return [site.site_name for site in obj.sites.all()]

    def validate(self, attrs):
        has_gst = attrs.get("has_gst", getattr(self.instance, "has_gst", False))
        gst_no = attrs.get("gst_no", getattr(self.instance, "gst_no", None))
        if has_gst and not gst_no:
            raise serializers.ValidationError(
                {"gst_no": "GST number is required when GST is Yes."}
            )

        return unique_name_validator(
            Model=IcwSupplierCreation,
            name_field="customer_name",
            scope_fields=[],
        )(self, attrs)

    def create(self, validated_data):
        sites = validated_data.pop("sites", [])
        validated_data.setdefault("is_active", True)
        instance = IcwSupplierCreation.objects.create(**validated_data)
        if sites:
            instance.sites.set(sites)
        return instance

    def update(self, instance, validated_data):
        sites = validated_data.pop("sites", None)
        instance = super().update(instance, validated_data)
        if sites is not None:
            instance.sites.set(sites)
        return instance
