from django.db import models

from shared.base_models import BaseMaster

from .country import Country
from .continent import Continent


class State(BaseMaster):
    
    continent_id = models.ForeignKey(
        Continent,
        on_delete=models.PROTECT,
        related_name="states",
        to_field="unique_id",
        db_column="continent_id",
    )

    country_id = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        related_name="states",
        to_field="unique_id",
        db_column="country_id",
    )

    name = models.CharField(max_length=100)
    label = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        ordering = ["id"]
        unique_together = ("country_id", "name")

    def __str__(self):
        return f"{self.name} ({self.country_id.name})"

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.is_active = False
        self.save(update_fields=["is_deleted", "is_active"])
