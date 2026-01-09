from django.db import models
from shared.base_models import BaseMaster
# from shared.utils import generate_site_id  # your ID generator


class Site(BaseMaster):

    # -------------------------
    # Core Site & Location
    # -------------------------
    site_name = models.CharField(max_length=150)
    state_id = models.CharField(max_length=100)
    district_id = models.CharField(max_length=100)
    ulb = models.CharField(max_length=100)
    site_address = models.TextField()
    status = models.CharField(max_length=20)

    # -------------------------
    # Geo Location
    # -------------------------
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # -------------------------
    # Project & Commercial
    # -------------------------
    project_value = models.DecimalField(max_digits=15, decimal_places=2)
    project_type_details = models.CharField(max_length=200)
    basic_payment_per_m3 = models.DecimalField(max_digits=10, decimal_places=2)
    dc_invoice_no = models.CharField(max_length=100)
    min_max_type = models.CharField(max_length=50)
    screen_name = models.CharField(max_length=100, null=True, blank=True)
    weighbridge_count = models.PositiveIntegerField(null=True, blank=True)

    # -------------------------
    # Electrical / Utility
    # -------------------------
    eb_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    unit_per_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    kwh = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    demand_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    eb_start_date = models.DateField(null=True, blank=True)
    eb_end_date = models.DateField(null=True, blank=True)

    # -------------------------
    # Zone / Capacity
    # -------------------------
    no_of_zones = models.PositiveIntegerField(null=True, blank=True)
    no_of_phases = models.PositiveIntegerField(null=True, blank=True)
    density_volume = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    extended_quantity = models.DecimalField(max_digits=10, decimal_places=2)

    # -------------------------
    # Charges
    # -------------------------
    service_charge = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    transportation_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # -------------------------
    # Bank & GST
    # -------------------------
    gst = models.CharField(max_length=50, null=True, blank=True)
    bank_name = models.CharField(max_length=150, null=True, blank=True)
    account_number = models.CharField(max_length=50, null=True, blank=True)
    ifsc_code = models.CharField(max_length=20, null=True, blank=True)
    bank_address = models.TextField(null=True, blank=True)

    # -------------------------
    # Project Lifecycle Dates
    # -------------------------
    erection_start_date = models.DateField(null=True, blank=True)
    commissioning_start_date = models.DateField(null=True, blank=True)
    project_completion_date = models.DateField(null=True, blank=True)

    # -------------------------
    # Documents
    # -------------------------
    weighment_folder_name = models.CharField(max_length=150, null=True, blank=True)
    verification_document = models.FileField(upload_to="site/verification/", null=True, blank=True)
    document_view = models.FileField(upload_to="site/documents/", null=True, blank=True)

    # -------------------------
    # Financial / Change
    # -------------------------
    petty_cash = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    proposed_change = models.TextField(null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.site_name
