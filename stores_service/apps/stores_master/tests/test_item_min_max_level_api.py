import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.stores_master.models.item_min_max_level_master import ItemMinMaxLevelMaster
from apps.stores_master.models.item_min_max_type_master import ItemMinMaxTypeMaster


class ItemMinMaxLevelMasterModelTests(TestCase):
    def setUp(self):
        self.item_type = ItemMinMaxTypeMaster.objects.create(type_name="Fast Moving")
        self.item_id = uuid.uuid4()

    def test_soft_delete_sets_flags_and_keeps_row(self):
        level = ItemMinMaxLevelMaster.objects.create(
            type=self.item_type,
            item_id=self.item_id,
            min_qty=10,
            max_qty=100,
            reorder=20,
        )
        level.delete()

        level.refresh_from_db()
        self.assertTrue(level.is_deleted)
        self.assertFalse(level.is_active)
        self.assertTrue(ItemMinMaxLevelMaster.objects.filter(pk=level.pk).exists())

    def test_str_includes_type_name(self):
        level = ItemMinMaxLevelMaster.objects.create(
            type=self.item_type,
            item_id=self.item_id,
            min_qty=10,
            max_qty=100,
            reorder=20,
        )
        self.assertIn("Fast Moving", str(level))


class ItemMinMaxLevelMasterApiTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="tester", password="pass1234")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.item_type = ItemMinMaxTypeMaster.objects.create(type_name="Fast Moving")
        self.other_item_type = ItemMinMaxTypeMaster.objects.create(type_name="Slow Moving")
        self.item_id = uuid.uuid4()
        self.other_item_id = uuid.uuid4()
        self.list_url = "/v1/stores-service/item-min-max-levels/"

    def test_unauthenticated_request_is_rejected(self):
        anon_client = APIClient()
        response = anon_client.get(self.list_url)
        self.assertIn(
            response.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )

    def test_create_item_min_max_level(self):
        response = self.client.post(
            self.list_url,
            {
                "type": str(self.item_type.unique_id),
                "item_id": str(self.item_id),
                "min_qty": "10.500",
                "max_qty": "100.000",
                "reorder": "20.250",
                "remarks": "Initial setup",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["type_name"], "Fast Moving")
        self.assertEqual(response.data["min_qty"], "10.500")
        self.assertTrue(response.data["is_active"])
        self.assertEqual(response.data["created_by"], "tester")

    def test_create_requires_type_and_item_id(self):
        response = self.client.post(
            self.list_url, {"min_qty": "1", "max_qty": "2", "reorder": "1"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("type", response.data)
        self.assertIn("item_id", response.data)

    def test_create_rejects_unknown_type(self):
        response = self.client.post(
            self.list_url,
            {
                "type": "00000000-0000-0000-0000-000000000000",
                "item_id": str(self.item_id),
                "min_qty": "1",
                "max_qty": "2",
                "reorder": "1",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("type", response.data)

    def test_duplicate_type_and_item_rejected(self):
        ItemMinMaxLevelMaster.objects.create(
            type=self.item_type, item_id=self.item_id, min_qty=1, max_qty=2, reorder=1
        )

        response = self.client.post(
            self.list_url,
            {
                "type": str(self.item_type.unique_id),
                "item_id": str(self.item_id),
                "min_qty": "5",
                "max_qty": "50",
                "reorder": "10",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("item_id", response.data)

    def test_same_item_allowed_under_different_type(self):
        ItemMinMaxLevelMaster.objects.create(
            type=self.item_type, item_id=self.item_id, min_qty=1, max_qty=2, reorder=1
        )

        response = self.client.post(
            self.list_url,
            {
                "type": str(self.other_item_type.unique_id),
                "item_id": str(self.item_id),
                "min_qty": "5",
                "max_qty": "50",
                "reorder": "10",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_different_item_allowed_under_same_type(self):
        ItemMinMaxLevelMaster.objects.create(
            type=self.item_type, item_id=self.item_id, min_qty=1, max_qty=2, reorder=1
        )

        response = self.client.post(
            self.list_url,
            {
                "type": str(self.item_type.unique_id),
                "item_id": str(self.other_item_id),
                "min_qty": "5",
                "max_qty": "50",
                "reorder": "10",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_editing_same_record_does_not_trigger_duplicate_error(self):
        level = ItemMinMaxLevelMaster.objects.create(
            type=self.item_type, item_id=self.item_id, min_qty=1, max_qty=2, reorder=1
        )
        detail_url = f"{self.list_url}{level.unique_id}/"

        response = self.client.patch(detail_url, {"min_qty": "3"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["min_qty"], "3.000")

    def test_list_levels(self):
        ItemMinMaxLevelMaster.objects.create(
            type=self.item_type, item_id=self.item_id, min_qty=1, max_qty=2, reorder=1
        )
        ItemMinMaxLevelMaster.objects.create(
            type=self.item_type, item_id=self.other_item_id, min_qty=1, max_qty=2, reorder=1
        )

        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_soft_deleted_levels_excluded_from_list(self):
        level = ItemMinMaxLevelMaster.objects.create(
            type=self.item_type, item_id=self.item_id, min_qty=1, max_qty=2, reorder=1
        )
        level.delete()

        response = self.client.get(self.list_url)
        self.assertEqual(response.data["count"], 0)

    def test_retrieve_level(self):
        level = ItemMinMaxLevelMaster.objects.create(
            type=self.item_type, item_id=self.item_id, min_qty=1, max_qty=2, reorder=1
        )
        detail_url = f"{self.list_url}{level.unique_id}/"

        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["item_id"], str(self.item_id))

    def test_update_status_toggle(self):
        level = ItemMinMaxLevelMaster.objects.create(
            type=self.item_type, item_id=self.item_id, min_qty=1, max_qty=2, reorder=1
        )
        detail_url = f"{self.list_url}{level.unique_id}/"

        response = self.client.patch(detail_url, {"is_active": False})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["is_active"])
        self.assertEqual(response.data["updated_by"], "tester")

    def test_delete_level_is_soft_delete_via_api(self):
        level = ItemMinMaxLevelMaster.objects.create(
            type=self.item_type, item_id=self.item_id, min_qty=1, max_qty=2, reorder=1
        )
        detail_url = f"{self.list_url}{level.unique_id}/"

        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        level.refresh_from_db()
        self.assertTrue(level.is_deleted)
        self.assertFalse(level.is_active)

        self.assertTrue(ItemMinMaxLevelMaster.objects.filter(pk=level.pk).exists())
