from rest_framework.routers import DefaultRouter
from django.urls import path

from apps.authentication.views.auth import (
    LoginView,
    LoginPageView,
    TokenRefreshView,
)
from apps.authentication.views.permission_and_role import (
    PermissionListView,
    MasterPermissionsView,
    UserRoleViewSet,
    UserRolePermissionsView,
    GroupPermissionViewSet,
)
from apps.authentication.views.user import UserViewSet

# Router (same style as common_master)
router = DefaultRouter()
router.register(r"user-role", UserRoleViewSet, basename="user-roles")
router.register(r"group-permission", GroupPermissionViewSet, basename="group-permissions")
router.register(r"user-creation", UserViewSet, basename="user-creations")

urlpatterns = router.urls + [

    #  Authentication
    path("login/", LoginView.as_view(), name="auth-login"),
    path("refresh/", TokenRefreshView.as_view(), name="token-refresh"),

    # Permissions
    path("permissions/", PermissionListView.as_view(), name="permission-list"),
    path("permissions/master/", MasterPermissionsView.as_view(), name="master-permissions"),

    # Role → Permission Mapping
    path(
        "roles/<uuid:role_id>/permissions/",
        UserRolePermissionsView.as_view(),
        name="role-permissions",
    ),
]
