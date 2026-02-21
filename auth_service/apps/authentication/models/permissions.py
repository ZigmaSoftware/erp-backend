"""
Permission Models for Master Service Access Control
=====================================================
These are proxy models (managed=False) that define custom permissions
for master service operations without creating database tables.

Each model provides CRUD permissions for the corresponding master entity.
"""

from django.db import models


class CountryAccess(models.Model):
    """Permissions for Country master data management."""
    class Meta:
        managed = False  # no table needed
        permissions = [
            ("master_country_create", "Can create country"),
            ("master_country_update", "Can update country"),
            ("master_country_delete", "Can delete country"),
            ("master_country_view", "Can view country"),
        ]


class StateAccess(models.Model):
    """Permissions for State master data management."""
    class Meta:
        managed = False  # no table needed
        permissions = [
            ("master_state_create", "Can create state"),
            ("master_state_update", "Can update state"),
            ("master_state_delete", "Can delete state"),
            ("master_state_view", "Can view state"),
        ]


class CityAccess(models.Model):
    """Permissions for City master data management."""
    class Meta:
        managed = False  # no table needed
        permissions = [
            ("master_city_create", "Can create city"),
            ("master_city_update", "Can update city"),
            ("master_city_delete", "Can delete city"),
            ("master_city_view", "Can view city"),
        ]


class DistrictAccess(models.Model):
    """Permissions for District master data management."""
    class Meta:
        managed = False  # no table needed
        permissions = [
            ("master_district_create", "Can create district"),
            ("master_district_update", "Can update district"),
            ("master_district_delete", "Can delete district"),
            ("master_district_view", "Can view district"),
        ]


class ContinentAccess(models.Model):
    """Permissions for Continent master data management."""
    class Meta:
        managed = False  # no table needed
        permissions = [
            ("master_continent_create", "Can create continent"),
            ("master_continent_update", "Can update continent"),
            ("master_continent_delete", "Can delete continent"),
            ("master_continent_view", "Can view continent"),
        ]


class PlantAccess(models.Model):
    """Permissions for Plant master data management."""
    class Meta:
        managed = False  # no table needed
        permissions = [
            ("master_plant_create", "Can create plant"),
            ("master_plant_update", "Can update plant"),
            ("master_plant_delete", "Can delete plant"),
            ("master_plant_view", "Can view plant"),
        ]


class SiteAccess(models.Model):
    """Permissions for Site master data management."""
    class Meta:
        managed = False  # no table needed
        permissions = [
            ("master_site_create", "Can create site"),
            ("master_site_update", "Can update site"),
            ("master_site_delete", "Can delete site"),
            ("master_site_view", "Can view site"),
        ]


class EquipmentTypeMasterAccess(models.Model):
    """Permissions for Equipment Type master data management."""
    class Meta:
        managed = False  # no table needed
        permissions = [
            ("master_equipment_type_create", "Can create equipment type"),
            ("master_equipment_type_update", "Can update equipment type"),
            ("master_equipment_type_delete", "Can delete equipment type"),
            ("master_equipment_type_view", "Can view equipment type"),
        ]
