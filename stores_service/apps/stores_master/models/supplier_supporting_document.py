from django.db import models

from shared.base_models import BaseMaster

from apps.stores_master.models.supplier_creation_master import SupplierCreationMaster


def supplier_supporting_document_upload_path(instance, filename):
    return f"supplier_creation/{instance.supplier_id}/{filename}"


class SupplierSupportingDocument(BaseMaster):

    class DocType(models.TextChoices):
        VENDOR_REGISTRATION = (
            "vendor_registration",
            "Vendor Registration Form with Aadhaar Card",
        )
        GENERAL_TERMS = "general_terms", "General Terms"
        DD_CHECKLIST = "dd_checklist", "DD Checklist"
        CANCELLED_CHEQUE = (
            "cancelled_cheque",
            "Copy of Unsigned Printed Cancelled Cheque",
        )
        PAN_CARD = "pan_card", "Copy of PAN Card Signed by Authorized Signatory"
        MSME_CERTIFICATE = "msme_certificate", "Copy of MSME Registration Certificate"
        GST_CERTIFICATE = "gst_certificate", "Copy of GST Registration Certificate"
        INCORPORATION_CERTIFICATE = (
            "incorporation_certificate",
            "Copy of Certificate of Incorporation / Shop & Establishment Certificate",
        )
        REGISTRATION_CERTIFICATES = (
            "registration_certificates",
            "Registration Certificates",
        )
        OTHERS = "others", "Others"

    supplier = models.ForeignKey(
        SupplierCreationMaster,
        on_delete=models.CASCADE,
        related_name="supporting_documents",
        to_field="unique_id",
        db_column="supplier_id",
    )
    doc_type = models.CharField(max_length=40, choices=DocType.choices)
    file = models.FileField(upload_to=supplier_supporting_document_upload_path)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.supplier.supplier_code} - {self.get_doc_type_display()}"

    def delete(self, *args, **kwargs):
        """
        Documents are attachments, not master data -- unlike every other model
        in this app, this is a real hard delete (matching the legacy
        file_upload_db.php?action=del_file_upld behavior), removing the
        physical file from storage too.
        """
        self.file.delete(save=False)
        super().delete(*args, **kwargs)
