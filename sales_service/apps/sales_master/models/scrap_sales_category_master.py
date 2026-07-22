from django.db import models
from django.db.models import Q

from shared.base_models import BaseMaster


class ScrapSalesCategoryMaster(BaseMaster):

    category_name = models.CharField(max_length=150)
    hsn_code = models.CharField(max_length=20)
    tax = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["category_name"]
        constraints = [
            models.UniqueConstraint(
                fields=["category_name"],
                condition=Q(is_deleted=False),
                name="uq_scrap_sales_category_name_active"
            ),
        ]

    def __str__(self):
        return self.category_name

    def delete(self, *args, **kwargs):
        """
        Soft delete
        """
        self.is_deleted = True
        self.is_active = False
        self.save(update_fields=["is_deleted", "is_active"])
