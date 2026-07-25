import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.stores_master.models.supplier_creation_master import SupplierCreationMaster


def _valid_payload(**overrides):
    payload = {
        "party_type": "creditor",
        "party_name": "Acme Traders",
        "mobile_no": "9876543210",
        "country_id": str(uuid.uuid4()),
        "state_id": str(uuid.uuid4()),
        "district_id": str(uuid.uuid4()),
        "city_id": str(uuid.uuid4()),
        "building_no": "12",
        "street": "Industrial Street",
        "area": "Industrial Area",
        "pincode": "600001",
        "sites": [str(uuid.uuid4())],
    }
    payload.update(overrides)
    return payload


class SupplierCreationMasterModelTests(TestCase):
    def _create(self, **overrides):
        defaults = dict(
            party_type="creditor",
            party_name="Acme Traders",
            mobile_no="9876543210",
            country_id=uuid.uuid4(),
            state_id=uuid.uuid4(),
            district_id=uuid.uuid4(),
            city_id=uuid.uuid4(),
            building_no="12",
            street="Industrial Street",
            area="Industrial Area",
            pincode="600001",
        )
        defaults.update(overrides)
        return SupplierCreationMaster.objects.create(**defaults)

    def test_supplier_code_is_auto_generated(self):
        supplier = self._create()
        self.assertTrue(supplier.supplier_code.startswith("SP"))

    def test_supplier_code_increments(self):
        first = self._create()
        second = self._create(party_name="Beta Traders", mobile_no="9876543211")

        first_suffix = int(first.supplier_code[2:])
        second_suffix = int(second.supplier_code[2:])
        self.assertEqual(second_suffix, first_suffix + 1)

    def test_soft_delete_sets_flags_and_keeps_row(self):
        supplier = self._create()
        supplier.delete()

        supplier.refresh_from_db()
        self.assertTrue(supplier.is_deleted)
        self.assertFalse(supplier.is_active)
        self.assertTrue(SupplierCreationMaster.objects.filter(pk=supplier.pk).exists())

    def test_str_includes_supplier_code_and_party_name(self):
        supplier = self._create()
        self.assertIn(supplier.supplier_code, str(supplier))
        self.assertIn("Acme Traders", str(supplier))


class SupplierCreationMasterApiTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="tester", password="pass1234")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.list_url = "/v1/stores-service/supplier-creations/"

    def test_unauthenticated_request_is_rejected(self):
        anon_client = APIClient()
        response = anon_client.get(self.list_url)
        self.assertIn(
            response.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )

    def test_create_supplier(self):
        response = self.client.post(self.list_url, _valid_payload(), format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["party_name"], "Acme Traders")
        self.assertTrue(response.data["supplier_code"].startswith("SP"))
        self.assertTrue(response.data["is_active"])
        self.assertEqual(response.data["created_by"], "tester")

    def test_create_requires_core_fields(self):
        response = self.client.post(self.list_url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        for field in (
            "party_type",
            "party_name",
            "mobile_no",
            "country_id",
            "state_id",
            "district_id",
            "city_id",
            "building_no",
            "street",
            "area",
            "pincode",
        ):
            self.assertIn(field, response.data)

    def test_create_requires_at_least_one_site(self):
        response = self.client.post(self.list_url, _valid_payload(sites=[]), format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("sites", response.data)

    def test_create_rejects_invalid_party_type(self):
        response = self.client.post(
            self.list_url, _valid_payload(party_type="unknown"), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("party_type", response.data)

    def test_gst_no_required_when_has_gst_true(self):
        response = self.client.post(
            self.list_url, _valid_payload(has_gst=True), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("gst_no", response.data)

    def test_gst_no_not_required_when_has_gst_false(self):
        response = self.client.post(
            self.list_url, _valid_payload(has_gst=False), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_succeeds_with_gst_no_when_has_gst_true(self):
        response = self.client.post(
            self.list_url,
            _valid_payload(has_gst=True, gst_no="29ABCDE1234F1Z5"),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_duplicate_party_name_and_mobile_rejected(self):
        self.client.post(self.list_url, _valid_payload(), format="json")

        response = self.client.post(
            self.list_url, _valid_payload(party_name="ACME TRADERS"), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("party_name", response.data)

    def test_same_party_name_allowed_with_different_mobile(self):
        self.client.post(self.list_url, _valid_payload(), format="json")

        response = self.client.post(
            self.list_url,
            _valid_payload(party_name="Acme Traders", mobile_no="9876500000"),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_editing_same_record_does_not_trigger_duplicate_error(self):
        create_response = self.client.post(self.list_url, _valid_payload(), format="json")
        detail_url = f"{self.list_url}{create_response.data['unique_id']}/"

        response = self.client.patch(
            detail_url, {"party_name": "Acme Traders"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_supplier_code_is_read_only(self):
        response = self.client.post(
            self.list_url, _valid_payload(supplier_code="SP999"), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotEqual(response.data["supplier_code"], "SP999")

    def test_list_suppliers(self):
        self.client.post(self.list_url, _valid_payload(), format="json")
        self.client.post(
            self.list_url,
            _valid_payload(party_name="Beta Traders", mobile_no="9876500001"),
            format="json",
        )

        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_soft_deleted_suppliers_excluded_from_list(self):
        create_response = self.client.post(self.list_url, _valid_payload(), format="json")
        detail_url = f"{self.list_url}{create_response.data['unique_id']}/"

        self.client.delete(detail_url)

        response = self.client.get(self.list_url)
        self.assertEqual(response.data["count"], 0)

    def test_update_status_toggle(self):
        create_response = self.client.post(self.list_url, _valid_payload(), format="json")
        detail_url = f"{self.list_url}{create_response.data['unique_id']}/"

        response = self.client.patch(detail_url, {"is_active": False}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["is_active"])
        self.assertEqual(response.data["updated_by"], "tester")

    def test_delete_supplier_is_soft_delete_via_api(self):
        create_response = self.client.post(self.list_url, _valid_payload(), format="json")
        detail_url = f"{self.list_url}{create_response.data['unique_id']}/"

        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        supplier = SupplierCreationMaster.objects.get(unique_id=create_response.data["unique_id"])
        self.assertTrue(supplier.is_deleted)
        self.assertFalse(supplier.is_active)
