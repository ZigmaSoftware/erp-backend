from django.db import models
from django.db.models import Q

from apps.common_master.models.site import Site
from shared.base_models import BaseMaster


class MailDetailsCreationMaster(BaseMaster):

    mail_type = models.CharField(max_length=50)
    mail_ids = models.TextField()
    site = models.ForeignKey(
        Site,
        on_delete=models.PROTECT,
        related_name="mail_details",
        to_field="unique_id",
        db_column="site_id",
    )

    class Meta:
        ordering = ["mail_type"]
        constraints = [
            models.UniqueConstraint(
                fields=["mail_type", "site"],
                condition=Q(is_deleted=False),
                name="uq_mail_details_type_site_active",
            ),
        ]

    def __str__(self):
        return f"{self.mail_type} - {self.site}"

    def delete(self, *args, **kwargs):
        """
        Soft delete
        """
        self.is_deleted = True
        self.is_active = False
        self.save(update_fields=["is_deleted", "is_active"])
