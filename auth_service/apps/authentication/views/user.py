from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from apps.authentication.serializers.user import (
    UserCreationSerializer,
    UserSerializer,
)


class UserViewSet(ModelViewSet):
    """Minimal ViewSet to create and list users and assign roles."""

    queryset = User.objects.all().order_by("id")
    authentication_classes = []
    permission_classes = []

    def get_serializer_class(self):
        if self.action in ("create",):
            return UserCreationSerializer
        return UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        out_serializer = UserSerializer(user)
        return Response(out_serializer.data, status=status.HTTP_201_CREATED)
