from rest_framework import serializers
from django.contrib.auth.models import User
from apps.authentication.models import UserRole


class UserCreationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    role_ids = serializers.ListField(
        child=serializers.UUIDField(), write_only=True, required=False
    )

    username = serializers.CharField(
        required=True,
        min_length=1,
        max_length=150,
        help_text="Required. 150 characters or fewer. Letters, digits, spaces and @/./+/-/_ only.",
    )

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "password",
            "email",
            "first_name",
            "last_name",
            "is_staff",
            "is_active",
            "role_ids",
        ]
        read_only_fields = ["id"]

    def create(self, validated_data):
        role_ids = validated_data.pop("role_ids", [])
        password = validated_data.pop("password")
        # username must be provided by user; enforce uniqueness and pattern in validation
        user = User(**validated_data)
        user.set_password(password)
        user.save()

        # Assign roles (UserRole → Group)
        for rid in role_ids:
            try:
                role = UserRole.objects.get(id=rid)
                group = role.group
                user.groups.add(group)
            except UserRole.DoesNotExist:
                # skip invalid role id
                continue

        return user

    def validate_username(self, value):
        """Validate username pattern and uniqueness."""
        import re

        # Pattern: letters, digits, spaces and @/./+/-/_ only
        pattern = r'^[\w.@+\- ]+$'
        if not re.match(pattern, value):
            raise serializers.ValidationError(
                "Enter a valid username. This value may contain only letters, numbers, and @/./+/-/_ characters."
            )

        # Enforce length already via field, ensure uniqueness
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("A user with that username already exists.")

        return value


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        required=True,
        min_length=1,
        max_length=150,
        help_text="Required. 150 characters or fewer. Letters, digits, spaces and @/./+/-/_ only.",
    )

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_staff",
            "is_active",
        ]
        read_only_fields = ["id"]

    def validate_username(self, value):
        """Validate username pattern and uniqueness."""
        import re

        # Pattern: letters, digits, spaces and @/./+/-/_ only
        pattern = r'^[\w.@+\- ]+$'
        if not re.match(pattern, value):
            raise serializers.ValidationError(
                "Enter a valid username. This value may contain only letters, numbers, spaces and @/./+/-/_ characters."
            )

        # Skip uniqueness check if updating the same user
        if self.instance and self.instance.username == value:
            return value

        # Ensure uniqueness for new users or changed usernames
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("A user with that username already exists.")

        return value
