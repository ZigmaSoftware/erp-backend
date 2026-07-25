from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.stores_master.models.unit_creation_master import UnitCreationMaster


class UnitCreationMasterModelTests(TestCase):
    def test_soft_delete_sets_flags_and_keeps_row(self):
        unit = UnitCreationMaster.objects.create(unit_name="Kilogram")
        unit.delete()

        unit.refresh_from_db()
        self.assertTrue(unit.is_deleted)
        self.assertFalse(unit.is_active)
        self.assertTrue(UnitCreationMaster.objects.filter(pk=unit.pk).exists())

    def test_str_returns_unit_name(self):
        unit = UnitCreationMaster.objects.create(unit_name="Litre")
        self.assertEqual(str(unit), "Litre")


class UnitCreationMasterApiTests(TestCase):
    def setUp(self):
        # REST_FRAMEWORK["TEST_REQUEST_DEFAULT_FORMAT"] = "json" in config/settings/test.py
        # makes this match how the real frontend posts (crudHelpers.ts uses axios JSON
        # requests, not multipart) -- with multipart/form parsing DRF's BooleanField
        # treats an absent field as an unchecked HTML checkbox (False) rather than
        # "use the model default" (True), which would give false failures here.
        User = get_user_model()
        self.user = User.objects.create_user(username="tester", password="pass1234")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.list_url = "/v1/stores-service/unit-creations/"

    def test_unauthenticated_request_is_rejected(self):
        anon_client = APIClient()
        response = anon_client.get(self.list_url)
        self.assertIn(
            response.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )

    def test_create_unit(self):
        response = self.client.post(
            self.list_url, {"unit_name": "Kilogram", "description": "Weight unit"}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["unit_name"], "Kilogram")
        self.assertTrue(response.data["is_active"])
        self.assertEqual(response.data["created_by"], "tester")

    def test_create_unit_without_description_succeeds(self):
        response = self.client.post(self.list_url, {"unit_name": "Metre"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_unit_requires_unit_name(self):
        response = self.client.post(self.list_url, {"description": "no name"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("unit_name", response.data)

    def test_duplicate_unit_name_case_insensitive_rejected(self):
        UnitCreationMaster.objects.create(unit_name="Kilogram")

        response = self.client.post(self.list_url, {"unit_name": "KILOGRAM"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("unit_name", response.data)

    def test_duplicate_rejection_uses_custom_validator_not_db_collation(self):
        # Regression guard: DRF auto-attaches a field-level UniqueValidator from
        # the model's UniqueConstraint, which (if not suppressed on the `unit_name`
        # field) would short-circuit before our unique_name_validator's explicit
        # __iexact check ever runs -- making the case-insensitive rule only appear
        # to work by accident of the DB column's collation. Assert our own
        # validator's message is what's actually returned.
        UnitCreationMaster.objects.create(unit_name="Kilogram")

        response = self.client.post(self.list_url, {"unit_name": "KILOGRAM"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("already exists in the selected scope", str(response.data["unit_name"]))

    def test_duplicate_check_is_global_not_scoped(self):
        # No acc_year / scope field exists any more; uniqueness must be table-wide.
        UnitCreationMaster.objects.create(unit_name="Box")
        response = self.client.post(self.list_url, {"unit_name": "box"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_name_reusable_after_soft_delete(self):
        unit = UnitCreationMaster.objects.create(unit_name="Kilogram")
        unit.delete()  # soft delete

        response = self.client.post(self.list_url, {"unit_name": "Kilogram"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_editing_same_record_does_not_trigger_duplicate_error(self):
        unit = UnitCreationMaster.objects.create(unit_name="Box")
        detail_url = f"{self.list_url}{unit.unique_id}/"

        response = self.client.patch(detail_url, {"unit_name": "Box"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_units(self):
        UnitCreationMaster.objects.create(unit_name="Kilogram")
        UnitCreationMaster.objects.create(unit_name="Litre")

        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_soft_deleted_units_excluded_from_list(self):
        unit = UnitCreationMaster.objects.create(unit_name="Kilogram")
        unit.delete()

        response = self.client.get(self.list_url)
        self.assertEqual(response.data["count"], 0)

    def test_retrieve_unit(self):
        unit = UnitCreationMaster.objects.create(unit_name="Kilogram")
        detail_url = f"{self.list_url}{unit.unique_id}/"

        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["unit_name"], "Kilogram")

    def test_update_status_toggle(self):
        unit = UnitCreationMaster.objects.create(unit_name="Kilogram")
        detail_url = f"{self.list_url}{unit.unique_id}/"

        response = self.client.patch(detail_url, {"is_active": False})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["is_active"])
        self.assertEqual(response.data["updated_by"], "tester")

    def test_delete_unit_is_soft_delete_via_api(self):
        unit = UnitCreationMaster.objects.create(unit_name="Kilogram")
        detail_url = f"{self.list_url}{unit.unique_id}/"

        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        unit.refresh_from_db()
        self.assertTrue(unit.is_deleted)
        self.assertFalse(unit.is_active)

        # Row still exists in DB (soft delete, not hard delete like legacy)
        self.assertTrue(UnitCreationMaster.objects.filter(pk=unit.pk).exists())
