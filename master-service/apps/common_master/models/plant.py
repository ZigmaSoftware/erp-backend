from django.db import models
from shared.base_models import BaseMaster

class Plant(BaseMaster):

    plant_name = models.CharField(max_length=150)
    site = models.ForeignKey('Site', to_field='unique_id', db_column='site_id', on_delete=models.PROTECT, related_name='plants')

    # -------------------------
    # Auto-generate unique_id
    # -------------------------
    def save(self, *args, **kwargs):
        # if not self.unique_id:
        #     self.unique_id = generate_site_id()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.plant_name