import uuid
from django.db import models

class BaseMaster(models.Model):
    unique_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    created_by = models.CharField(max_length=40, null=True, blank=True)
    updated_by = models.CharField(max_length=40, null=True, blank=True)

    class Meta:
        abstract = True
