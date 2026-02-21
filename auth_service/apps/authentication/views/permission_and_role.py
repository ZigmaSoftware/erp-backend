"""
Permission and User Role Views
===============================
API views for managing permissions and user roles.
"""

from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.contrib.auth.models import Permission, Group
from apps.authentication.models import UserRole
from apps.authentication.serializers.permission_and_role import (
    PermissionSerializer,
    UserRoleSerializer,
    UserRoleDetailSerializer,
    GroupSerializer,
    GroupPermissionSerializer,
    GroupPermissionDetailSerializer,
)


class PermissionListView(APIView):
    """
    List all available permissions in the system.
    
    Retrieve a list of all permissions, optionally filtered by codename.
    Supports filtering by permission codename pattern (e.g., 'master_country').
    """
    
    authentication_classes = []
    permission_classes = []

    @swagger_auto_schema(
        operation_summary="List all permissions",
        operation_description="Get all permissions in the system with optional filtering by codename",
        manual_parameters=[
            openapi.Parameter(
                'codename',
                openapi.IN_QUERY,
                description='Filter permissions by codename pattern (case-insensitive)',
                type=openapi.TYPE_STRING,
                required=False,
            ),
        ],
        responses={
            200: openapi.Response(
                description='List of permissions',
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                            'codename': openapi.Schema(type=openapi.TYPE_STRING),
                            'name': openapi.Schema(type=openapi.TYPE_STRING),
                            'content_type': openapi.Schema(type=openapi.TYPE_INTEGER),
                        }
                    )
                )
            )
        }
    )
    def get(self, request):
        """Get all permissions, optionally filtered by codename pattern."""
        codename_filter = request.query_params.get("codename", "")
        
        permissions = Permission.objects.all()
        
        if codename_filter:
            permissions = permissions.filter(codename__icontains=codename_filter)
        
        serializer = PermissionSerializer(permissions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MasterPermissionsView(APIView):
    """
    Get all master service permissions grouped by entity.
    
    Returns permissions for master service operations (country, state, city, etc.)
    grouped by entity type with CRUD operations (create, read, update, delete).
    """
    
    authentication_classes = []
    permission_classes = []

    @swagger_auto_schema(
        operation_summary="List master service permissions",
        operation_description="Get all master service permissions grouped by entity (country, state, city, etc.)",
        responses={
            200: openapi.Response(
                description='Master permissions grouped by entity',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    additionalProperties=openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'codename': openapi.Schema(type=openapi.TYPE_STRING),
                                'name': openapi.Schema(type=openapi.TYPE_STRING),
                                'content_type': openapi.Schema(type=openapi.TYPE_INTEGER),
                            }
                        )
                    )
                )
            )
        }
    )
    def get(self, request):
        """Get all master service permissions."""
        permissions = Permission.objects.filter(
            codename__startswith="master_"
        ).order_by("codename")
        
        # Group by entity (country, state, city, etc.)
        grouped = {}
        for perm in permissions:
            # Extract entity name from codename
            # e.g., "master_country_create" → "country"
            parts = perm.codename.split("_")
            if len(parts) >= 3:
                entity = parts[1]
                if entity not in grouped:
                    grouped[entity] = []
                grouped[entity].append(PermissionSerializer(perm).data)
        
        return Response(grouped, status=status.HTTP_200_OK)


class UserRoleViewSet(ModelViewSet):
    """
    API endpoint for managing user roles.
    
    Provides full CRUD operations for user roles with support for:
    - Listing roles with filtering and search
    - Creating new roles
    - Retrieving detailed role information
    - Updating existing roles
    - Soft delete (deactivate) with option for hard delete
    
    List/Filter:
        - is_active: Filter by active status (true/false)
        - name: Filter by role name pattern
        - search: Search in name and description
        - ordering: Sort by name or created_at
    
    Example requests:
        GET    /api/auth/roles/?is_active=true&ordering=name
        POST   /api/auth/roles/ {"name": "admin", "description": "Admin role"}
        GET    /api/auth/roles/{id}/
        PUT    /api/auth/roles/{id}/ {"description": "Updated description"}
        DELETE /api/auth/roles/{id}/?hard_delete=true
    """
    
    queryset = UserRole.objects.all()
    serializer_class = UserRoleSerializer
    permission_classes = []
    authentication_classes = []
    lookup_field = "id"
    filterset_fields = ["is_active", "name"]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]

    def get_serializer_class(self):
        """Use detailed serializer for retrieve."""
        if self.action == "retrieve":
            return UserRoleDetailSerializer
        return UserRoleSerializer

    @swagger_auto_schema(
        operation_summary="Create a new user role",
        operation_description="Create a new user role with name and optional description",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['name'],
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING, description='Unique role name'),
                'description': openapi.Schema(type=openapi.TYPE_STRING, description='Role description'),
                'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Active status'),
            }
        ),
        responses={
            201: UserRoleSerializer,
            400: openapi.Response(description='Invalid request data'),
        }
    )
    def create(self, request, *args, **kwargs):
        """Create a new role."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        """Save the role."""
        serializer.save()

    @swagger_auto_schema(
        operation_summary="Delete/deactivate a user role",
        operation_description="Delete or deactivate a user role. By default performs soft delete (sets is_active=False). Add ?hard_delete=true to permanently delete.",
        manual_parameters=[
            openapi.Parameter(
                'hard_delete',
                openapi.IN_QUERY,
                description='Perform hard delete instead of soft delete (default: false)',
                type=openapi.TYPE_BOOLEAN,
                required=False,
            ),
        ],
        responses={
            200: openapi.Response(description='Role deactivated'),
            204: openapi.Response(description='Role deleted'),
            404: openapi.Response(description='Role not found'),
        }
    )
    def destroy(self, request, *args, **kwargs):
        """Soft delete a role (set is_active=False)."""
        instance = self.get_object()
        
        # Use soft delete by default
        use_hard_delete = request.query_params.get("hard_delete", "false").lower() == "true"
        
        if use_hard_delete:
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            # Soft delete
            instance.is_active = False
            instance.save()
            return Response(
                {"message": f"Role '{instance.name}' deactivated"},
                status=status.HTTP_200_OK,
            )


class UserRolePermissionsView(APIView):
    """
    Manage permissions for a specific user role.
    
    Operations:
        GET    /api/auth/roles/{id}/permissions/      - Get role permissions
        POST   /api/auth/roles/{id}/permissions/      - Add permissions to role
        DELETE /api/auth/roles/{id}/permissions/      - Remove permissions from role
    
    Request body for POST/DELETE:
        {
            "permission_ids": [1, 2, 3, ...]
        }
    """
    
    authentication_classes = []
    permission_classes = []

    @swagger_auto_schema(
        operation_summary="Get role permissions",
        operation_description="Retrieve all permissions assigned to a specific user role",
        responses={
            200: openapi.Response(
                description='Role permissions',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'role_id': openapi.Schema(type=openapi.TYPE_STRING, format='uuid'),
                        'role_name': openapi.Schema(type=openapi.TYPE_STRING),
                        'permissions': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(type=openapi.TYPE_STRING)
                        ),
                    }
                )
            ),
            404: openapi.Response(description='Role not found'),
        }
    )
    def get(self, request, role_id):
        """Get all permissions assigned to a role."""
        try:
            role = UserRole.objects.get(id=role_id)
        except UserRole.DoesNotExist:
            return Response(
                {"error": "Role not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        # TODO: Implement once UserRole is linked to auth.Group
        # For now, return empty permissions
        return Response(
            {
                "role_id": str(role.id),
                "role_name": role.name,
                "permissions": [],
            },
            status=status.HTTP_200_OK,
        )

    @swagger_auto_schema(
        operation_summary="Add permissions to role",
        operation_description="Assign permissions to a user role",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['permission_ids'],
            properties={
                'permission_ids': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_INTEGER),
                    description='List of permission IDs to add'
                ),
            }
        ),
        responses={
            200: openapi.Response(description='Permissions updated'),
            400: openapi.Response(description='Invalid request data'),
            404: openapi.Response(description='Role not found'),
        }
    )
    def post(self, request, role_id):
        """Add permissions to a role."""
        try:
            role = UserRole.objects.get(id=role_id)
        except UserRole.DoesNotExist:
            return Response(
                {"error": "Role not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        permission_ids = request.data.get("permission_ids", [])
        
        if not permission_ids:
            return Response(
                {"error": "permission_ids list is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        # TODO: Implement once UserRole is linked to auth.Group
        return Response(
            {"message": "Permissions updated"},
            status=status.HTTP_200_OK,
        )

    @swagger_auto_schema(
        operation_summary="Remove permissions from role",
        operation_description="Revoke permissions from a user role",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['permission_ids'],
            properties={
                'permission_ids': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_INTEGER),
                    description='List of permission IDs to remove'
                ),
            }
        ),
        responses={
            200: openapi.Response(description='Permissions removed'),
            400: openapi.Response(description='Invalid request data'),
            404: openapi.Response(description='Role not found'),
        }
    )
    def delete(self, request, role_id):
        """Remove permissions from a role."""
        try:
            role = UserRole.objects.get(id=role_id)
        except UserRole.DoesNotExist:
            return Response(
                {"error": "Role not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        permission_ids = request.data.get("permission_ids", [])
        
        if not permission_ids:
            return Response(
                {"error": "permission_ids list is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        # TODO: Implement once UserRole is linked to auth.Group
        return Response(
            {"message": "Permissions removed"},
            status=status.HTTP_200_OK,
        )


class GroupPermissionViewSet(ViewSet):
    """
    ViewSet for managing Group (Role) and Permission assignments.
    
    Directly manages the auth_group_permissions table without a separate model.
    
    Features:
    - Dropdown selection of Groups/Roles
    - Multi-select field for Permissions
    - Properly handles many-to-many relationships
    - Multiple permissions per group, multiple groups per permission
    
    Endpoints:
        GET    /api/auth/group-permissions/            - List all group permission details
        POST   /api/auth/group-permissions/            - Assign permissions to a group
        GET    /api/auth/group-permissions/groups/     - List all available groups
        GET    /api/auth/group-permissions/permissions/ - List all available permissions
        GET    /api/auth/group-permissions/by-group/{group_id}/ - Get permissions for specific group
        DELETE /api/auth/group-permissions/remove/{group_id}/    - Remove all permissions from group
    """
    
    authentication_classes = []
    permission_classes = []

    @swagger_auto_schema(
        operation_summary="List all groups with their permissions",
        operation_description="Get all groups and their assigned permissions",
        responses={
            200: openapi.Response(
                description='List of groups with permissions',
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_OBJECT)
                )
            ),
        }
    )
    def list(self, request):
        """Get all groups with their permissions."""
        groups = Group.objects.all()
        data = []
        for group in groups:
            permissions = group.permissions.all()
            data.append({
                'group_id': group.id,
                'group_name': group.name,
                'permissions': PermissionSerializer(permissions, many=True).data
            })
        return Response(data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Assign permissions to a group",
        operation_description="Add permissions to a group. This ADDS to existing permissions, not replaces them.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['group_id', 'permission_ids'],
            properties={
                'group_id': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='Group ID'
                ),
                'permission_ids': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_INTEGER),
                    description='List of permission IDs to assign'
                ),
            }
        ),
        responses={
            201: openapi.Response(description='Permissions assigned successfully'),
            400: openapi.Response(description='Invalid request data'),
            404: openapi.Response(description='Group or permission not found'),
        }
    )
    def create(self, request):
        """Assign permissions to a group."""
        serializer = GroupPermissionSerializer(data=request.data)
        if serializer.is_valid():
            result = serializer.save()
            return Response(result, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="List all available groups",
        operation_description="Get all groups available for selection in dropdown",
        responses={
            200: openapi.Response(
                description='List of groups',
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_OBJECT)
                )
            ),
        }
    )
    @action(detail=False, methods=['get'])
    def groups(self, request):
        """Get all available groups for dropdown."""
        groups = Group.objects.all()
        serializer = GroupSerializer(groups, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="List all available permissions",
        operation_description="Get all permissions available for multi-select field",
        responses={
            200: openapi.Response(
                description='List of permissions',
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_OBJECT)
                )
            ),
        }
    )
    @action(detail=False, methods=['get'])
    def permissions(self, request):
        """Get all available permissions for multi-select."""
        permissions = Permission.objects.all().order_by('codename')
        serializer = PermissionSerializer(permissions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Get permissions for a specific group",
        operation_description="Retrieve all permissions assigned to a group",
        responses={
            200: openapi.Response(
                description='Group permissions',
                schema=openapi.Schema(type=openapi.TYPE_OBJECT)
            ),
            404: openapi.Response(description='Group not found'),
        }
    )
    @action(detail=False, methods=['get'], url_path='by-group/(?P<group_id>[^/.]+)')
    def by_group(self, request, group_id=None):
        """Get permissions for a specific group."""
        try:
            group = Group.objects.get(id=group_id)
        except Group.DoesNotExist:
            return Response(
                {"error": "Group not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        permissions = group.permissions.all()
        return Response(
            {
                'group_id': group.id,
                'group_name': group.name,
                'permissions': PermissionSerializer(permissions, many=True).data
            },
            status=status.HTTP_200_OK,
        )

    @swagger_auto_schema(
        operation_summary="Remove all permissions from a group",
        operation_description="Clear all permissions assigned to a group",
        responses={
            200: openapi.Response(description='Permissions removed'),
            404: openapi.Response(description='Group not found'),
        }
    )
    @action(detail=False, methods=['delete'], url_path='remove/(?P<group_id>[^/.]+)')
    def remove(self, request, group_id=None):
        """Remove all permissions from a group."""
        try:
            group = Group.objects.get(id=group_id)
        except Group.DoesNotExist:
            return Response(
                {"error": "Group not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        group.permissions.clear()
        return Response(
            {
                "message": "All permissions removed from group",
                "group_id": group.id,
                "group_name": group.name
            },
            status=status.HTTP_200_OK,
        )



