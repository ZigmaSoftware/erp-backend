from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.stores_master.models.item_min_max_type_master import ItemMinMaxTypeMaster


class ItemMinMaxTypeMasterModelTests(TestCase):
    def test_soft_delete_sets_flags_and_keeps_row(self):
        item_type = ItemMinMaxTypeMaster.objects.create(type_name="Fast Moving")
        item_type.delete()

        item_type.refresh_from_db()
        self.assertTrue(item_type.is_deleted)
        self.assertFalse(item_type.is_active)
        self.assertTrue(ItemMinMaxTypeMaster.objects.filter(pk=item_type.pk).exists())

    def test_str_returns_type_name(self):
        item_type = ItemMinMaxTypeMaster.objects.create(type_name="Slow Moving")
        self.assertEqual(str(item_type), "Slow Moving")


class ItemMinMaxTypeMasterApiTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="tester", password="pass1234")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.list_url = "/v1/stores-service/item-min-max-types/"

    def test_unauthenticated_request_is_rejected(self):
        anon_client = APIClient()
        response = anon_client.get(self.list_url)
        self.assertIn(
            response.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )

    def test_create_item_min_max_type(self):
        response = self.client.post(
            self.list_url,
            {"type_name": "Fast Moving", "type_description": "High turnover items"},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["type_name"], "Fast Moving")
        self.assertTrue(response.data["is_active"])
        self.assertEqual(response.data["created_by"], "tester")

    def test_create_item_min_max_type_without_description_succeeds(self):
        response = self.client.post(self.list_url, {"type_name": "Slow Moving"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_item_min_max_type_requires_type_name(self):
        response = self.client.post(self.list_url, {"type_description": "no name"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("type_name", response.data)

    def test_duplicate_type_name_case_insensitive_rejected(self):
        ItemMinMaxTypeMaster.objects.create(type_name="Fast Moving")

        response = self.client.post(self.list_url, {"type_name": "FAST MOVING"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("type_name", response.data)

    def test_duplicate_rejection_uses_custom_validator_not_db_collation(self):
        ItemMinMaxTypeMaster.objects.create(type_name="Fast Moving")

        response = self.client.post(self.list_url, {"type_name": "FAST MOVING"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("already exists in the selected scope", str(response.data["type_name"]))

    def test_name_reusable_after_soft_delete(self):
        item_type = ItemMinMaxTypeMaster.objects.create(type_name="Fast Moving")
        item_type.delete()

        response = self.client.post(self.list_url, {"type_name": "Fast Moving"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_editing_same_record_does_not_trigger_duplicate_error(self):
        item_type = ItemMinMaxTypeMaster.objects.create(type_name="Fast Moving")
        detail_url = f"{self.list_url}{item_type.unique_id}/"

        response = self.client.patch(detail_url, {"type_name": "Fast Moving"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_item_min_max_types(self):
        ItemMinMaxTypeMaster.objects.create(type_name="Fast Moving")
        ItemMinMaxTypeMaster.objects.create(type_name="Slow Moving")

        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_soft_deleted_types_excluded_from_list(self):
        item_type = ItemMinMaxTypeMaster.objects.create(type_name="Fast Moving")
        item_type.delete()

        response = self.client.get(self.list_url)
        self.assertEqual(response.data["count"], 0)

    def test_retrieve_item_min_max_type(self):
        item_type = ItemMinMaxTypeMaster.objects.create(type_name="Fast Moving")
        detail_url = f"{self.list_url}{item_type.unique_id}/"

        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["type_name"], "Fast Moving")

    def test_update_status_toggle(self):
        item_type = ItemMinMaxTypeMaster.objects.create(type_name="Fast Moving")
        detail_url = f"{self.list_url}{item_type.unique_id}/"

        response = self.client.patch(detail_url, {"is_active": False})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["is_active"])
        self.assertEqual(response.data["updated_by"], "tester")

    def test_delete_item_min_max_type_is_soft_delete_via_api(self):
        item_type = ItemMinMaxTypeMaster.objects.create(type_name="Fast Moving")
        detail_url = f"{self.list_url}{item_type.unique_id}/"

        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        item_type.refresh_from_db()
        self.assertTrue(item_type.is_deleted)
        self.assertFalse(item_type.is_active)

        self.assertTrue(ItemMinMaxTypeMaster.objects.filter(pk=item_type.pk).exists())
