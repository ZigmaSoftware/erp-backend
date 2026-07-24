from decimal import Decimal

from rest_framework import serializers

from apps.common_master.models.site import Site
from apps.sales_master.models.rdf_inerts_perc_entry import (
    RdfInertsPercEntry,
    RdfInertsPercEntrySub,
)


class RdfInertsPercEntrySubSerializer(serializers.ModelSerializer):
    site_display_name = serializers.CharField(source="site_name", read_only=True)

    class Meta:
        model = RdfInertsPercEntrySub
        fields = "__all__"
        read_only_fields = (
            "unique_id",
            "random_sc",
            "random_no",
            "ri_perc_entry_no",
            "site_name",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "site_display_name",
        )

    def validate_perc_item_percentage(self, value):
        if value < Decimal("0") or value > Decimal("100"):
            raise serializers.ValidationError("Percentage must be between 0 and 100.")
        return value


class RdfInertsPercEntrySerializer(serializers.ModelSerializer):
    site_name = serializers.CharField()
    site_id = serializers.SerializerMethodField()
    site_display_name = serializers.CharField(source="site_name", read_only=True)
    items = serializers.SerializerMethodField()
    items_data = RdfInertsPercEntrySubSerializer(
        many=True,
        write_only=True,
        required=False,
    )

    class Meta:
        model = RdfInertsPercEntry
        fields = "__all__"
        read_only_fields = (
            "unique_id",
            "random_sc",
            "random_no",
            "ri_perc_entry_no",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "site_id",
            "site_display_name",
            "items",
        )
        validators = []

    def get_site_id(self, obj):
        site = Site.objects.filter(site_name=obj.site_name, is_deleted=False).first()
        return str(site.unique_id) if site else ""

    def get_items(self, obj):
        details = RdfInertsPercEntrySub.objects.filter(
            random_sc=obj.random_sc,
            random_no=obj.random_no,
            ri_perc_entry_no=obj.ri_perc_entry_no,
            is_deleted=False,
        )
        return RdfInertsPercEntrySubSerializer(details, many=True).data

    def validate_perc_item_percentage(self, value):
        if value < Decimal("0") or value > Decimal("100"):
            raise serializers.ValidationError("Percentage must be between 0 and 100.")
        return value

    def validate(self, attrs):
        items = attrs.get("items_data", None)
        if not self.instance and not items:
            raise serializers.ValidationError(
                {"items_data": "At least one RDF/Inerts percentage row is required."}
            )
        site_value = attrs.get("site_name")
        if site_value:
            attrs["site_name"] = self._resolve_site_name(site_value)
        return attrs

    def _resolve_site_name(self, value):
        site = Site.objects.filter(unique_id=value, is_deleted=False).first()
        if site:
            return site.site_name
        return value

    def _sync_items(self, instance, items_data, username=None):
        RdfInertsPercEntrySub.objects.filter(
            random_sc=instance.random_sc,
            random_no=instance.random_no,
            ri_perc_entry_no=instance.ri_perc_entry_no,
            is_deleted=False,
        ).update(
            is_deleted=True,
            is_active=False,
            updated_by=username,
        )

        rows = []
        for item in items_data:
            rows.append(
                RdfInertsPercEntrySub(
                    random_sc=instance.random_sc,
                    random_no=instance.random_no,
                    ri_perc_entry_no=instance.ri_perc_entry_no,
                    site_name=instance.site_name,
                    perc_date=item["perc_date"],
                    perc_item_name=item["perc_item_name"],
                    perc_item_percentage=item["perc_item_percentage"],
                    perc_status=item.get("perc_status", True),
                    is_active=item.get("perc_status", True),
                    created_by=username,
                )
            )
        RdfInertsPercEntrySub.objects.bulk_create(rows)

    def _apply_first_item_to_parent(self, validated_data, items_data):
        if not items_data:
            return

        first_item = items_data[0]
        validated_data["perc_date"] = first_item["perc_date"]
        validated_data["perc_item_name"] = first_item["perc_item_name"]
        validated_data["perc_item_percentage"] = first_item["perc_item_percentage"]
        validated_data["perc_status"] = first_item.get("perc_status", True)
        validated_data["is_active"] = first_item.get("perc_status", True)

    def create(self, validated_data):
        items_data = validated_data.pop("items_data", [])
        self._apply_first_item_to_parent(validated_data, items_data)
        validated_data.setdefault("is_active", True)
        instance = RdfInertsPercEntry.objects.create(**validated_data)
        self._sync_items(
            instance,
            items_data,
            username=validated_data.get("created_by"),
        )
        return instance

    def update(self, instance, validated_data):
        items_data = validated_data.pop("items_data", None)
        if items_data is not None:
            self._apply_first_item_to_parent(validated_data, items_data)

        instance = super().update(instance, validated_data)

        if items_data is not None:
            self._sync_items(
                instance,
                items_data,
                username=validated_data.get("updated_by"),
            )

        return instance
