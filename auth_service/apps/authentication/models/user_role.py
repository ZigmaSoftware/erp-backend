import uuid
from django.db import models
from django.contrib.auth.models import Group


class UserRole(models.Model):
    """
    ERP-facing Role model mapped 1:1 to Django auth.Group.
    Uses UUID as public identifier.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    group = models.OneToOneField(
        Group,
        on_delete=models.CASCADE,
        related_name="user_role"
    )

    name = models.CharField(
        max_length=150,
        unique=True,
        db_index=True
    )

    description = models.TextField(blank=True, default="")

    is_active = models.BooleanField(default=True, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_roles"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["is_active", "name"]),
        ]

    def __str__(self):
        return self.name
    def save(self, *args, **kwargs):
        """
        Override save to automatically create/update the linked auth.Group.
        """
        # Auto-create or update the linked auth.Group
        if not self.group_id:
            # Create new Group if it doesn't exist
            self.group, created = Group.objects.get_or_create(name=self.name)
        else:
            # Update existing Group name if UserRole name changed
            self.group.name = self.name
            self.group.save()
        
        # Normalize name to lowercase
        self.name = self.name.lower()
        
        super().save(*args, **kwargs)