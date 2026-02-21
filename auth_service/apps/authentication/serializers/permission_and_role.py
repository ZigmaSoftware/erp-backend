"""
Permission and User Role Serializers
=====================================
Serializers for permission and user role models.
"""

from rest_framework import serializers
from django.contrib.auth.models import Permission, Group
from apps.authentication.models import UserRole


class PermissionSerializer(serializers.ModelSerializer):
    """Serializer for Django Permission model.
    
    Represents a system permission that can be assigned to roles.
    
    Fields:
        id: Permission ID
        codename: Permission code (e.g., 'master_country_create')
        name: Human-readable permission name
        content_type: Content type ID (model the permission relates to)
    """
    
    class Meta:
        model = Permission
        fields = ["id", "codename", "name", "content_type"]
        read_only_fields = ["id", "content_type"]


class GroupSerializer(serializers.ModelSerializer):
    """Serializer for Django Group (role) model."""
    
    class Meta:
        model = Group
        fields = ["id", "name"]
        read_only_fields = ["id"]


class UserRoleSerializer(serializers.ModelSerializer):
    """Serializer for UserRole model."""
    
    class Meta:
        model = UserRole
        fields = [
            "id",
            "name",
            "description",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
    
    def validate_name(self, value):
        """Ensure role name is unique (case-insensitive)."""
        queryset = UserRole.objects.filter(name__iexact=value)
        
        # If updating, exclude the current instance
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise serializers.ValidationError(
                f"A role with the name '{value}' already exists."
            )
        return value.lower()


class UserRoleDetailSerializer(UserRoleSerializer):
    """Extended serializer for UserRole with permission details."""
    
    permissions = serializers.SerializerMethodField()
    
    class Meta(UserRoleSerializer.Meta):
        fields = UserRoleSerializer.Meta.fields + ["permissions"]
    
    def get_permissions(self, obj):
        """Get all permissions associated with this role."""
        permissions = []
        return permissions


class GroupPermissionSerializer(serializers.Serializer):
    """
    Serializer for managing Group permissions.
    
    This serializer manages the relationship between Groups and Permissions
    by directly interacting with Django's auth_group_permissions table.
    
    Features:
    - Dropdown selection of Groups
    - Multi-select field for Permissions
    - Saves directly to auth_group_permissions (no separate model needed)
    - Properly handles many-to-many relationships
    """
    
    # Dropdown field for selecting a group
    group_id = serializers.IntegerField(
        help_text="Select a role/group from dropdown"
    )
    
    # Multi-select field for permissions
    permission_ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="Select permissions for this role"
    )
    
    def validate_group_id(self, value):
        """Validate that the group exists."""
        if not Group.objects.filter(id=value).exists():
            raise serializers.ValidationError("Group with this ID does not exist.")
        return value

    def validate_permission_ids(self, value):
        """Validate that all permissions exist."""
        if not value:
            raise serializers.ValidationError("At least one permission must be selected.")
        
        # Check if all permission IDs exist
        existing_perms = Permission.objects.filter(id__in=value).count()
        if existing_perms != len(value):
            raise serializers.ValidationError("One or more permission IDs do not exist.")
        return value

    def create(self, validated_data):
        """Create/update group permissions in auth_group_permissions table."""
        group_id = validated_data['group_id']
        permission_ids = validated_data['permission_ids']
        
        group = Group.objects.get(id=group_id)
        permissions = Permission.objects.filter(id__in=permission_ids)
        
        # Add permissions (doesn't remove existing ones if not in the list)
        group.permissions.add(*permissions)
        
        return {
            'group_id': group_id,
            'group_name': group.name,
            'permission_ids': permission_ids,
            'message': 'Permissions added successfully'
        }

    def update(self, instance, validated_data):
        """This serializer is used for create/POST only."""
        raise NotImplementedError("Use create instead")


class GroupPermissionDetailSerializer(serializers.Serializer):
    """
    Read-only serializer for displaying group permissions.
    Shows all current permissions for a group.
    """
    
    group_id = serializers.IntegerField(read_only=True)
    group_name = serializers.CharField(read_only=True)
    permissions = PermissionSerializer(many=True, read_only=True)
