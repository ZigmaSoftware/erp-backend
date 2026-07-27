from django.db import models

from shared.base_models import BaseMaster


class DocumentTypeMaster(BaseMaster):

    class DisposalType(models.TextChoices):
        CUSTOMER_SCOPE = "customer_scope", "Customer Scope"
        ZIGMA_SCOPE = "zigma_scope", "Zigma Scope"
        TRANSPORT_SCOPE = "transport_scope", "Transport Scope"

    disposal_type = models.CharField(
        max_length=20,
        choices=DisposalType.choices,
        default=DisposalType.CUSTOMER_SCOPE,
    )
    doc_type = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["doc_type"]

    def __str__(self):
        return self.doc_type

    def delete(self, *args, **kwargs):
        """
        Soft delete
        """
        self.is_deleted = True
        self.is_active = False
        self.save(update_fields=["is_deleted", "is_active"])
