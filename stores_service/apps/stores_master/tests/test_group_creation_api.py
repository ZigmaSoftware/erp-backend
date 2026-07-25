from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.stores_master.models.group_creation_master import GroupCreationMaster


class GroupCreationMasterModelTests(TestCase):
    def test_soft_delete_sets_flags_and_keeps_row(self):
        group = GroupCreationMaster.objects.create(group_name="Fasteners")
        group.delete()

        group.refresh_from_db()
        self.assertTrue(group.is_deleted)
        self.assertFalse(group.is_active)
        self.assertTrue(GroupCreationMaster.objects.filter(pk=group.pk).exists())

    def test_str_returns_group_name(self):
        group = GroupCreationMaster.objects.create(group_name="Electricals")
        self.assertEqual(str(group), "Electricals")


class GroupCreationMasterApiTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="tester", password="pass1234")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.list_url = "/v1/stores-service/group-creations/"

    def test_unauthenticated_request_is_rejected(self):
        anon_client = APIClient()
        response = anon_client.get(self.list_url)
        self.assertIn(
            response.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )

    def test_create_group(self):
        response = self.client.post(
            self.list_url, {"group_name": "Fasteners", "description": "Nuts and bolts"}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["group_name"], "Fasteners")
        self.assertTrue(response.data["is_active"])
        self.assertEqual(response.data["created_by"], "tester")

    def test_create_group_without_description_succeeds(self):
        response = self.client.post(self.list_url, {"group_name": "Electricals"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_group_requires_group_name(self):
        response = self.client.post(self.list_url, {"description": "no name"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("group_name", response.data)

    def test_duplicate_group_name_case_insensitive_rejected(self):
        GroupCreationMaster.objects.create(group_name="Fasteners")

        response = self.client.post(self.list_url, {"group_name": "FASTENERS"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("group_name", response.data)

    def test_duplicate_rejection_uses_custom_validator_not_db_collation(self):
        GroupCreationMaster.objects.create(group_name="Fasteners")

        response = self.client.post(self.list_url, {"group_name": "FASTENERS"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("already exists in the selected scope", str(response.data["group_name"]))

    def test_name_reusable_after_soft_delete(self):
        group = GroupCreationMaster.objects.create(group_name="Fasteners")
        group.delete()

        response = self.client.post(self.list_url, {"group_name": "Fasteners"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_editing_same_record_does_not_trigger_duplicate_error(self):
        group = GroupCreationMaster.objects.create(group_name="Electricals")
        detail_url = f"{self.list_url}{group.unique_id}/"

        response = self.client.patch(detail_url, {"group_name": "Electricals"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_groups(self):
        GroupCreationMaster.objects.create(group_name="Fasteners")
        GroupCreationMaster.objects.create(group_name="Electricals")

        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_soft_deleted_groups_excluded_from_list(self):
        group = GroupCreationMaster.objects.create(group_name="Fasteners")
        group.delete()

        response = self.client.get(self.list_url)
        self.assertEqual(response.data["count"], 0)

    def test_retrieve_group(self):
        group = GroupCreationMaster.objects.create(group_name="Fasteners")
        detail_url = f"{self.list_url}{group.unique_id}/"

        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["group_name"], "Fasteners")

    def test_update_status_toggle(self):
        group = GroupCreationMaster.objects.create(group_name="Fasteners")
        detail_url = f"{self.list_url}{group.unique_id}/"

        response = self.client.patch(detail_url, {"is_active": False})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["is_active"])
        self.assertEqual(response.data["updated_by"], "tester")

    def test_delete_group_is_soft_delete_via_api(self):
        group = GroupCreationMaster.objects.create(group_name="Fasteners")
        detail_url = f"{self.list_url}{group.unique_id}/"

        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        group.refresh_from_db()
        self.assertTrue(group.is_deleted)
        self.assertFalse(group.is_active)

        self.assertTrue(GroupCreationMaster.objects.filter(pk=group.pk).exists())
