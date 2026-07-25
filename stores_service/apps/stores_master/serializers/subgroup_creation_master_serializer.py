from rest_framework import serializers

from apps.stores_master.models.group_creation_master import GroupCreationMaster
from apps.stores_master.models.subgroup_creation_master import SubGroupCreationMaster
from shared.validators import unique_name_validator


class SubGroupCreationMasterSerializer(serializers.ModelSerializer):

    group = serializers.SlugRelatedField(
        slug_field="unique_id",
        queryset=GroupCreationMaster.objects.filter(is_deleted=False),
        error_messages={"does_not_exist": "Invalid group."},
    )

    group_name = serializers.CharField(source="group.group_name", read_only=True)

    # DRF auto-attaches a field-level UniqueValidator from the model's
    # UniqueConstraint, which runs before (and short-circuits) validate()
    # below -- overriding it here with validators=[] ensures the explicit
    # case-insensitive check in validate() is what actually enforces
    # uniqueness, rather than relying on the DB column's collation.
    subgroup_name = serializers.CharField(max_length=100, validators=[])

    class Meta:
        model = SubGroupCreationMaster
        fields = "__all__"
        read_only_fields = (
            "unique_id",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "group_name",
        )
        validators = []

    def validate(self, attrs):
        return unique_name_validator(
            Model=SubGroupCreationMaster,
            name_field="subgroup_name",
            scope_fields=["group"],
        )(self, attrs)

    def create(self, validated_data):
        validated_data.setdefault("is_active", True)
        return super().create(validated_data)
