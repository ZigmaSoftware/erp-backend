from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.stores_master.models.task_creation_master import TaskCreationMaster


class TaskCreationMasterModelTests(TestCase):
    def test_soft_delete_sets_flags_and_keeps_row(self):
        task = TaskCreationMaster.objects.create(
            task_type=TaskCreationMaster.TaskType.CAPEX, task_name="New Excavator"
        )
        task.delete()

        task.refresh_from_db()
        self.assertTrue(task.is_deleted)
        self.assertFalse(task.is_active)
        self.assertTrue(TaskCreationMaster.objects.filter(pk=task.pk).exists())

    def test_str_includes_task_type_display(self):
        task = TaskCreationMaster.objects.create(
            task_type=TaskCreationMaster.TaskType.OPEX, task_name="Fuel Purchase"
        )
        self.assertEqual(str(task), "Fuel Purchase (Opex)")


class TaskCreationMasterApiTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="tester", password="pass1234")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.list_url = "/v1/stores-service/task-creations/"

    def test_unauthenticated_request_is_rejected(self):
        anon_client = APIClient()
        response = anon_client.get(self.list_url)
        self.assertIn(
            response.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )

    def test_create_task(self):
        response = self.client.post(
            self.list_url,
            {
                "task_type": "capex",
                "task_name": "New Excavator",
                "description": "Purchase of new excavator",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["task_name"], "New Excavator")
        self.assertEqual(response.data["task_type"], "capex")
        self.assertTrue(response.data["is_active"])
        self.assertEqual(response.data["created_by"], "tester")

    def test_create_task_without_description_succeeds(self):
        response = self.client.post(
            self.list_url, {"task_type": "opex", "task_name": "Fuel Purchase"}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_task_requires_task_name_and_task_type(self):
        response = self.client.post(self.list_url, {"description": "no name or type"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("task_name", response.data)
        self.assertIn("task_type", response.data)

    def test_create_task_rejects_invalid_task_type(self):
        response = self.client.post(
            self.list_url, {"task_type": "unknown", "task_name": "New Excavator"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("task_type", response.data)

    def test_duplicate_task_name_within_same_type_rejected(self):
        TaskCreationMaster.objects.create(task_type="capex", task_name="New Excavator")

        response = self.client.post(
            self.list_url, {"task_type": "capex", "task_name": "NEW EXCAVATOR"}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("task_name", response.data)

    def test_same_task_name_allowed_under_different_type(self):
        TaskCreationMaster.objects.create(task_type="capex", task_name="New Excavator")

        response = self.client.post(
            self.list_url, {"task_type": "opex", "task_name": "New Excavator"}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_editing_same_record_does_not_trigger_duplicate_error(self):
        task = TaskCreationMaster.objects.create(task_type="capex", task_name="New Excavator")
        detail_url = f"{self.list_url}{task.unique_id}/"

        response = self.client.patch(
            detail_url, {"task_type": "capex", "task_name": "New Excavator"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_tasks(self):
        TaskCreationMaster.objects.create(task_type="capex", task_name="New Excavator")
        TaskCreationMaster.objects.create(task_type="opex", task_name="Fuel Purchase")

        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_soft_deleted_tasks_excluded_from_list(self):
        task = TaskCreationMaster.objects.create(task_type="capex", task_name="New Excavator")
        task.delete()

        response = self.client.get(self.list_url)
        self.assertEqual(response.data["count"], 0)

    def test_retrieve_task(self):
        task = TaskCreationMaster.objects.create(task_type="capex", task_name="New Excavator")
        detail_url = f"{self.list_url}{task.unique_id}/"

        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["task_name"], "New Excavator")

    def test_update_status_toggle(self):
        task = TaskCreationMaster.objects.create(task_type="capex", task_name="New Excavator")
        detail_url = f"{self.list_url}{task.unique_id}/"

        response = self.client.patch(detail_url, {"is_active": False})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["is_active"])
        self.assertEqual(response.data["updated_by"], "tester")

    def test_delete_task_is_soft_delete_via_api(self):
        task = TaskCreationMaster.objects.create(task_type="capex", task_name="New Excavator")
        detail_url = f"{self.list_url}{task.unique_id}/"

        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        task.refresh_from_db()
        self.assertTrue(task.is_deleted)
        self.assertFalse(task.is_active)

        self.assertTrue(TaskCreationMaster.objects.filter(pk=task.pk).exists())
