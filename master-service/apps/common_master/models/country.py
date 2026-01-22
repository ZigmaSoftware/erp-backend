from django.db import models

from shared.base_models import BaseMaster

from .continent import Continent


class Country(BaseMaster):

    continent_id = models.ForeignKey(
        Continent,
        on_delete=models.PROTECT,
        related_name="countries",
        to_field="unique_id"
    )

    name = models.CharField(max_length=100)
    currency = models.CharField(max_length=20, null=True)
    mob_code = models.CharField(max_length=5, null=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.is_active = False
        self.save(update_fields=["is_deleted", "is_active"])
