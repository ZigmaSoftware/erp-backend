from django.db import models

from shared.base_models import BaseMaster

from .country import Country
from .state import State
from .continent import Continent


class District(BaseMaster):
    
    continent_id = models.ForeignKey(
        Continent,
        on_delete=models.PROTECT,
        related_name="districts",
        to_field="unique_id",
        db_column="continent_id",
    )

    country_id = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        related_name="districts",
        to_field="unique_id",
        db_column="country_id",
    )

    state_id = models.ForeignKey(
        State,
        on_delete=models.PROTECT,
        related_name="districts",
        to_field="unique_id",
        db_column="state_id",
    )

    name = models.CharField(max_length=100)

    class Meta:
        ordering = ["name"]
        unique_together = ("state_id", "name")   # FIXED

    def __str__(self):
        return f"{self.name} ({self.state_id.name})"

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.is_active = False
        self.save(update_fields=["is_deleted", "is_active"])
