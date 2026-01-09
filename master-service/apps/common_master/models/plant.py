from django.db import models
from shared.base_models import BaseMaster

class Plant(BaseMaster):

    plant_name = models.CharField(max_length=150)
    site_id = models.ForeignKey('Site', to_field='unique_id', db_column='site_id', on_delete=models.PROTECT, related_name='plants')

    def __str__(self):
        return self.plant_name
