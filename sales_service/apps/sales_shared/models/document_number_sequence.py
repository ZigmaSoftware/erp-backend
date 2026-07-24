from django.db import models


class DocumentNumberSequence(models.Model):
    """
    Database-backed atomic sequence generator for document numbers.
    Uses select_for_update() to prevent concurrent duplicates.

    Each row = a counter for prefix + site_code + year_month.
    Example: prefix='WO', site_code='HO', year_month='2607' -> WO-HO-2607-0001
    """

    prefix = models.CharField(max_length=20)
    site_code = models.CharField(max_length=10, blank=True, default="")
    year_month = models.CharField(max_length=6)
    last_sequence = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["prefix", "site_code", "year_month"]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.prefix}-{self.site_code}-{self.year_month} seq={self.last_sequence}"
