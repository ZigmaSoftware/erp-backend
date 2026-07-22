from django.db import models
from django.db.models import Q

from shared.base_models import BaseMaster


class TermsOfPaymentCreationMaster(BaseMaster):

    terms_of_payment = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["terms_of_payment"]
        constraints = [
            models.UniqueConstraint(
                fields=["terms_of_payment"],
                condition=Q(is_deleted=False),
                name="uq_terms_of_payment_name_active",
            ),
        ]

    def __str__(self):
        return self.terms_of_payment

    def delete(self, *args, **kwargs):
        """
        Soft delete
        """
        self.is_deleted = True
        self.is_active = False
        self.save(update_fields=["is_deleted", "is_active"])
