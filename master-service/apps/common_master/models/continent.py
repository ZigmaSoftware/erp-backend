from django.db import models

from shared.base_models import BaseMaster


class Continent(BaseMaster):

    name = models.CharField(max_length=100)

    class Meta:
        # Keep paginated results ordered by creation/id sequence
        ordering = ["id"]

    def __str__(self):
        return self.name

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.is_active = False
        self.save(update_fields=["is_deleted", "is_active"])
