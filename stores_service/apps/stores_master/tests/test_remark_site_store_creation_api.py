from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.stores_master.models.remark_site_store_creation_master import (
    RemarkSiteStoreCreationMaster,
)


class RemarkSiteStoreCreationMasterModelTests(TestCase):
    def test_soft_delete_sets_flags_and_keeps_row(self):
        remark = RemarkSiteStoreCreationMaster.objects.create(remark_type="Damaged")
        remark.delete()

        remark.refresh_from_db()
        self.assertTrue(remark.is_deleted)
        self.assertFalse(remark.is_active)
        self.assertTrue(RemarkSiteStoreCreationMaster.objects.filter(pk=remark.pk).exists())

    def test_str_returns_remark_type(self):
        remark = RemarkSiteStoreCreationMaster.objects.create(remark_type="Shortage")
        self.assertEqual(str(remark), "Shortage")


class RemarkSiteStoreCreationMasterApiTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="tester", password="pass1234")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.list_url = "/v1/stores-service/remark-site-store-creations/"

    def test_unauthenticated_request_is_rejected(self):
        anon_client = APIClient()
        response = anon_client.get(self.list_url)
        self.assertIn(
            response.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )

    def test_create_remark(self):
        response = self.client.post(
            self.list_url,
            {"remark_type": "Damaged", "description": "Item received in damaged condition"},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["remark_type"], "Damaged")
        self.assertTrue(response.data["is_active"])
        self.assertEqual(response.data["created_by"], "tester")

    def test_create_remark_without_description_succeeds(self):
        response = self.client.post(self.list_url, {"remark_type": "Shortage"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_remark_requires_remark_type(self):
        response = self.client.post(self.list_url, {"description": "no type"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("remark_type", response.data)

    def test_duplicate_remark_type_case_insensitive_rejected(self):
        RemarkSiteStoreCreationMaster.objects.create(remark_type="Damaged")

        response = self.client.post(self.list_url, {"remark_type": "DAMAGED"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("remark_type", response.data)

    def test_duplicate_rejection_uses_custom_validator_not_db_collation(self):
        RemarkSiteStoreCreationMaster.objects.create(remark_type="Damaged")

        response = self.client.post(self.list_url, {"remark_type": "DAMAGED"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("already exists in the selected scope", str(response.data["remark_type"]))

    def test_name_reusable_after_soft_delete(self):
        remark = RemarkSiteStoreCreationMaster.objects.create(remark_type="Damaged")
        remark.delete()

        response = self.client.post(self.list_url, {"remark_type": "Damaged"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_editing_same_record_does_not_trigger_duplicate_error(self):
        remark = RemarkSiteStoreCreationMaster.objects.create(remark_type="Shortage")
        detail_url = f"{self.list_url}{remark.unique_id}/"

        response = self.client.patch(detail_url, {"remark_type": "Shortage"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_remarks(self):
        RemarkSiteStoreCreationMaster.objects.create(remark_type="Damaged")
        RemarkSiteStoreCreationMaster.objects.create(remark_type="Shortage")

        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_soft_deleted_remarks_excluded_from_list(self):
        remark = RemarkSiteStoreCreationMaster.objects.create(remark_type="Damaged")
        remark.delete()

        response = self.client.get(self.list_url)
        self.assertEqual(response.data["count"], 0)

    def test_retrieve_remark(self):
        remark = RemarkSiteStoreCreationMaster.objects.create(remark_type="Damaged")
        detail_url = f"{self.list_url}{remark.unique_id}/"

        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["remark_type"], "Damaged")

    def test_update_status_toggle(self):
        remark = RemarkSiteStoreCreationMaster.objects.create(remark_type="Damaged")
        detail_url = f"{self.list_url}{remark.unique_id}/"

        response = self.client.patch(detail_url, {"is_active": False})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["is_active"])
        self.assertEqual(response.data["updated_by"], "tester")

    def test_delete_remark_is_soft_delete_via_api(self):
        remark = RemarkSiteStoreCreationMaster.objects.create(remark_type="Damaged")
        detail_url = f"{self.list_url}{remark.unique_id}/"

        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        remark.refresh_from_db()
        self.assertTrue(remark.is_deleted)
        self.assertFalse(remark.is_active)

        self.assertTrue(RemarkSiteStoreCreationMaster.objects.filter(pk=remark.pk).exists())
