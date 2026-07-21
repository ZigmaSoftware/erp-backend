from django.db import models
from django.db.models import Q

from shared.base_models import BaseMaster


class DocumentTypeMaster(BaseMaster):

    doc_type = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["doc_type"]
        constraints = [
            models.UniqueConstraint(
                fields=["doc_type"],
                condition=Q(is_deleted=False),
                name="uq_doc_type_name_active"
            ),
        ]

    def __str__(self):
        return self.doc_type

    def delete(self, *args, **kwargs):
        """
        Soft delete
        """
        self.is_deleted = True
        self.is_active = False
        self.save(update_fields=["is_deleted", "is_active"])
