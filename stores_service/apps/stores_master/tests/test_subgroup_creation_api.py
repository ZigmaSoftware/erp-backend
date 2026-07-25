from django.contrib.auth import get_user_model
from django.db.models import ProtectedError
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.stores_master.models.group_creation_master import GroupCreationMaster
from apps.stores_master.models.subgroup_creation_master import SubGroupCreationMaster


class SubGroupCreationMasterModelTests(TestCase):
    def setUp(self):
        self.group = GroupCreationMaster.objects.create(group_name="Fasteners")

    def test_soft_delete_sets_flags_and_keeps_row(self):
        subgroup = SubGroupCreationMaster.objects.create(
            group=self.group, subgroup_name="Bolts"
        )
        subgroup.delete()

        subgroup.refresh_from_db()
        self.assertTrue(subgroup.is_deleted)
        self.assertFalse(subgroup.is_active)
        self.assertTrue(SubGroupCreationMaster.objects.filter(pk=subgroup.pk).exists())

    def test_str_returns_subgroup_name(self):
        subgroup = SubGroupCreationMaster.objects.create(
            group=self.group, subgroup_name="Bolts"
        )
        self.assertEqual(str(subgroup), "Bolts")

    def test_group_hard_delete_is_protected_while_subgroups_exist(self):
        # GroupCreationMaster.delete() is overridden to soft-delete and never
        # reaches Django's FK collector, so PROTECT is only observable via a
        # real hard delete (e.g. queryset.delete(), Django admin bulk delete).
        SubGroupCreationMaster.objects.create(group=self.group, subgroup_name="Bolts")
        with self.assertRaises(ProtectedError):
            GroupCreationMaster.objects.filter(pk=self.group.pk).delete()


class SubGroupCreationMasterApiTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="tester", password="pass1234")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.group = GroupCreationMaster.objects.create(group_name="Fasteners")
        self.other_group = GroupCreationMaster.objects.create(group_name="Electricals")
        self.list_url = "/v1/stores-service/subgroup-creations/"

    def test_unauthenticated_request_is_rejected(self):
        anon_client = APIClient()
        response = anon_client.get(self.list_url)
        self.assertIn(
            response.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )

    def test_create_subgroup(self):
        response = self.client.post(
            self.list_url,
            {
                "group": str(self.group.unique_id),
                "subgroup_name": "Bolts",
                "description": "Threaded fasteners",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["subgroup_name"], "Bolts")
        self.assertEqual(response.data["group_name"], "Fasteners")
        self.assertTrue(response.data["is_active"])
        self.assertEqual(response.data["created_by"], "tester")

    def test_create_subgroup_requires_group(self):
        response = self.client.post(self.list_url, {"subgroup_name": "Bolts"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("group", response.data)

    def test_create_subgroup_rejects_unknown_group(self):
        response = self.client.post(
            self.list_url,
            {"group": "00000000-0000-0000-0000-000000000000", "subgroup_name": "Bolts"},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("group", response.data)

    def test_duplicate_subgroup_name_within_same_group_rejected(self):
        SubGroupCreationMaster.objects.create(group=self.group, subgroup_name="Bolts")

        response = self.client.post(
            self.list_url,
            {"group": str(self.group.unique_id), "subgroup_name": "BOLTS"},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("subgroup_name", response.data)

    def test_same_subgroup_name_allowed_in_different_group(self):
        SubGroupCreationMaster.objects.create(group=self.group, subgroup_name="Bolts")

        response = self.client.post(
            self.list_url,
            {"group": str(self.other_group.unique_id), "subgroup_name": "Bolts"},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_editing_same_record_does_not_trigger_duplicate_error(self):
        subgroup = SubGroupCreationMaster.objects.create(
            group=self.group, subgroup_name="Bolts"
        )
        detail_url = f"{self.list_url}{subgroup.unique_id}/"

        response = self.client.patch(
            detail_url, {"group": str(self.group.unique_id), "subgroup_name": "Bolts"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_subgroups(self):
        SubGroupCreationMaster.objects.create(group=self.group, subgroup_name="Bolts")
        SubGroupCreationMaster.objects.create(group=self.group, subgroup_name="Nuts")

        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_soft_deleted_subgroups_excluded_from_list(self):
        subgroup = SubGroupCreationMaster.objects.create(
            group=self.group, subgroup_name="Bolts"
        )
        subgroup.delete()

        response = self.client.get(self.list_url)
        self.assertEqual(response.data["count"], 0)

    def test_retrieve_subgroup(self):
        subgroup = SubGroupCreationMaster.objects.create(
            group=self.group, subgroup_name="Bolts"
        )
        detail_url = f"{self.list_url}{subgroup.unique_id}/"

        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["subgroup_name"], "Bolts")

    def test_update_status_toggle(self):
        subgroup = SubGroupCreationMaster.objects.create(
            group=self.group, subgroup_name="Bolts"
        )
        detail_url = f"{self.list_url}{subgroup.unique_id}/"

        response = self.client.patch(detail_url, {"is_active": False})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["is_active"])
        self.assertEqual(response.data["updated_by"], "tester")

    def test_delete_subgroup_is_soft_delete_via_api(self):
        subgroup = SubGroupCreationMaster.objects.create(
            group=self.group, subgroup_name="Bolts"
        )
        detail_url = f"{self.list_url}{subgroup.unique_id}/"

        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        subgroup.refresh_from_db()
        self.assertTrue(subgroup.is_deleted)
        self.assertFalse(subgroup.is_active)

        self.assertTrue(SubGroupCreationMaster.objects.filter(pk=subgroup.pk).exists())
