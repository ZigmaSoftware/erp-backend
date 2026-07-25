import shutil
import tempfile
import uuid

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APIClient

from apps.stores_master.models.supplier_creation_master import SupplierCreationMaster
from apps.stores_master.models.supplier_supporting_document import (
    SupplierSupportingDocument,
)

MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class SupplierSupportingDocumentApiTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="tester", password="pass1234")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.supplier = SupplierCreationMaster.objects.create(
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
        self.list_url = "/v1/stores-service/supplier-supporting-documents/"

    def _upload_file(self, name="cheque.pdf"):
        return SimpleUploadedFile(name, b"file-bytes", content_type="application/pdf")

    def test_unauthenticated_request_is_rejected(self):
        anon_client = APIClient()
        response = anon_client.get(self.list_url)
        self.assertIn(
            response.status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )

    def test_upload_document(self):
        response = self.client.post(
            self.list_url,
            {
                "supplier": str(self.supplier.unique_id),
                "doc_type": "cancelled_cheque",
                "file": self._upload_file(),
            },
            format="multipart",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["doc_type"], "cancelled_cheque")
        self.assertEqual(response.data["created_by"], "tester")

    def test_upload_requires_supplier_doc_type_and_file(self):
        response = self.client.post(self.list_url, {}, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("supplier", response.data)
        self.assertIn("doc_type", response.data)
        self.assertIn("file", response.data)

    def test_upload_rejects_invalid_doc_type(self):
        response = self.client.post(
            self.list_url,
            {
                "supplier": str(self.supplier.unique_id),
                "doc_type": "unknown_type",
                "file": self._upload_file(),
            },
            format="multipart",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("doc_type", response.data)

    def test_upload_rejects_unknown_supplier(self):
        response = self.client.post(
            self.list_url,
            {
                "supplier": str(uuid.uuid4()),
                "doc_type": "others",
                "file": self._upload_file(),
            },
            format="multipart",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("supplier", response.data)

    def test_list_filters_by_supplier(self):
        other_supplier = SupplierCreationMaster.objects.create(
            party_type="creditor",
            party_name="Beta Traders",
            mobile_no="9876500000",
            country_id=uuid.uuid4(),
            state_id=uuid.uuid4(),
            district_id=uuid.uuid4(),
            city_id=uuid.uuid4(),
            building_no="1",
            street="Street",
            area="Area",
            pincode="600002",
        )
        SupplierSupportingDocument.objects.create(
            supplier=self.supplier, doc_type="others", file=self._upload_file("a.pdf")
        )
        SupplierSupportingDocument.objects.create(
            supplier=other_supplier, doc_type="others", file=self._upload_file("b.pdf")
        )

        response = self.client.get(self.list_url, {"supplier": str(self.supplier.unique_id)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_delete_document_is_hard_delete_and_removes_file(self):
        document = SupplierSupportingDocument.objects.create(
            supplier=self.supplier,
            doc_type="cancelled_cheque",
            file=self._upload_file(),
        )
        file_path = document.file.path
        detail_url = f"{self.list_url}{document.unique_id}/"

        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertFalse(
            SupplierSupportingDocument.objects.filter(pk=document.pk).exists()
        )
        self.assertFalse(document.file.storage.exists(file_path))

    def test_deleting_supplier_does_not_cascade_soft_delete(self):
        # SupplierCreationMaster.delete() is a soft delete that never reaches
        # Django's FK collector, so documents survive a normal API delete of
        # the parent supplier -- only a real hard delete would cascade.
        SupplierSupportingDocument.objects.create(
            supplier=self.supplier, doc_type="others", file=self._upload_file()
        )
        self.supplier.delete()

        self.assertEqual(
            SupplierSupportingDocument.objects.filter(supplier=self.supplier).count(), 1
        )
