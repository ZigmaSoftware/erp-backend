from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """Profile linked 1:1 to Django auth.User."""

    user = models.OneToOneField(
        User,
        on_delete=models.PROTECT,
        related_name="profile",
    )

    employee_id = models.CharField(max_length=50, blank=True, default="")
    phone = models.CharField(max_length=20, blank=True, default="")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_profiles"
        ordering = ["user_id"]

    def __str__(self):
        return f"{self.user.username} profile"
