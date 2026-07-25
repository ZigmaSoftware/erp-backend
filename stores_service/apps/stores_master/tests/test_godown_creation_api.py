import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.stores_master.models.godown_creation_master import GodownCreationMaster


class GodownCreationMasterModelTests(TestCase):
    def setUp(self):
        self.site_id = uuid.uuid4()

    def test_soft_delete_sets_flags_and_keeps_row(self):
        godown = GodownCreationMaster.objects.create(
            site_id=self.site_id, godown_name="Main Godown"
        )
        godown.delete()

        godown.refresh_from_db()
        self.assertTrue(godown.is_deleted)
        self.assertFalse(godown.is_active)
        self.assertTrue(GodownCreationMaster.objects.filter(pk=godown.pk).exists())

    def test_str_returns_godown_name(self):
        godown = GodownCreationMaster.objects.create(
            site_id=self.site_id, godown_name="Main Godown"
        )
        self.assertEqual(str(godown), "Main Godown")


class GodownCreationMasterApiTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="tester", password="pass1234")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.site_id = uuid.uuid4()
        self.other_site_id = uuid.uuid4()
        self.list_url = "/v1/stores-service/godown-creations/"

    def test_unauthenticated_request_is_rejected(self):
        anon_client = APIClient()
        response = anon_client.get(self.list_url)
        self.assertIn(
            response.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )

    def test_create_godown(self):
        response = self.client.post(
            self.list_url,
            {
                "site_id": str(self.site_id),
                "godown_name": "Main Godown",
                "godown_address": "Plot 12, Industrial Area",
                "description": "Primary storage godown",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["godown_name"], "Main Godown")
        self.assertEqual(response.data["site_id"], str(self.site_id))
        self.assertTrue(response.data["is_active"])
        self.assertEqual(response.data["created_by"], "tester")

    def test_create_godown_without_address_or_description_succeeds(self):
        response = self.client.post(
            self.list_url, {"site_id": str(self.site_id), "godown_name": "Main Godown"}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_requires_site_id_and_godown_name(self):
        response = self.client.post(self.list_url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("site_id", response.data)
        self.assertIn("godown_name", response.data)

    def test_duplicate_godown_name_within_same_site_rejected(self):
        GodownCreationMaster.objects.create(site_id=self.site_id, godown_name="Main Godown")

        response = self.client.post(
            self.list_url, {"site_id": str(self.site_id), "godown_name": "MAIN GODOWN"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("godown_name", response.data)

    def test_same_godown_name_allowed_under_different_site(self):
        GodownCreationMaster.objects.create(site_id=self.site_id, godown_name="Main Godown")

        response = self.client.post(
            self.list_url, {"site_id": str(self.other_site_id), "godown_name": "Main Godown"}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_editing_same_record_does_not_trigger_duplicate_error(self):
        godown = GodownCreationMaster.objects.create(
            site_id=self.site_id, godown_name="Main Godown"
        )
        detail_url = f"{self.list_url}{godown.unique_id}/"

        response = self.client.patch(
            detail_url, {"site_id": str(self.site_id), "godown_name": "Main Godown"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_godowns(self):
        GodownCreationMaster.objects.create(site_id=self.site_id, godown_name="Main Godown")
        GodownCreationMaster.objects.create(site_id=self.site_id, godown_name="Overflow Godown")

        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_soft_deleted_godowns_excluded_from_list(self):
        godown = GodownCreationMaster.objects.create(
            site_id=self.site_id, godown_name="Main Godown"
        )
        godown.delete()

        response = self.client.get(self.list_url)
        self.assertEqual(response.data["count"], 0)

    def test_retrieve_godown(self):
        godown = GodownCreationMaster.objects.create(
            site_id=self.site_id, godown_name="Main Godown"
        )
        detail_url = f"{self.list_url}{godown.unique_id}/"

        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["godown_name"], "Main Godown")

    def test_update_status_toggle(self):
        godown = GodownCreationMaster.objects.create(
            site_id=self.site_id, godown_name="Main Godown"
        )
        detail_url = f"{self.list_url}{godown.unique_id}/"

        response = self.client.patch(detail_url, {"is_active": False})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["is_active"])
        self.assertEqual(response.data["updated_by"], "tester")

    def test_delete_godown_is_soft_delete_via_api(self):
        godown = GodownCreationMaster.objects.create(
            site_id=self.site_id, godown_name="Main Godown"
        )
        detail_url = f"{self.list_url}{godown.unique_id}/"

        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        godown.refresh_from_db()
        self.assertTrue(godown.is_deleted)
        self.assertFalse(godown.is_active)

        self.assertTrue(GodownCreationMaster.objects.filter(pk=godown.pk).exists())
