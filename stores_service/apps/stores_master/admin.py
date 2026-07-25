from django.contrib import admin

from apps.stores_master.models.unit_creation_master import UnitCreationMaster
from apps.stores_master.models.group_creation_master import GroupCreationMaster
from apps.stores_master.models.subgroup_creation_master import SubGroupCreationMaster
from apps.stores_master.models.item_min_max_type_master import ItemMinMaxTypeMaster
from apps.stores_master.models.item_min_max_level_master import ItemMinMaxLevelMaster
from apps.stores_master.models.main_task_creation_master import MainTaskCreationMaster
from apps.stores_master.models.task_creation_master import TaskCreationMaster
from apps.stores_master.models.godown_creation_master import GodownCreationMaster
from apps.stores_master.models.supplier_creation_master import SupplierCreationMaster
from apps.stores_master.models.supplier_supporting_document import (
    SupplierSupportingDocument,
)
from apps.stores_master.models.remark_site_store_creation_master import (
    RemarkSiteStoreCreationMaster,
)


@admin.register(UnitCreationMaster)
class UnitCreationMasterAdmin(admin.ModelAdmin):
    list_display = ("unit_name", "is_active", "created_at")
    search_fields = ("unit_name",)
    list_filter = ("is_active",)


@admin.register(GroupCreationMaster)
class GroupCreationMasterAdmin(admin.ModelAdmin):
    list_display = ("group_name", "is_active", "created_at")
    search_fields = ("group_name",)
    list_filter = ("is_active",)


@admin.register(SubGroupCreationMaster)
class SubGroupCreationMasterAdmin(admin.ModelAdmin):
    list_display = ("subgroup_name", "group", "is_active", "created_at")
    search_fields = ("subgroup_name",)
    list_filter = ("is_active", "group")


@admin.register(ItemMinMaxTypeMaster)
class ItemMinMaxTypeMasterAdmin(admin.ModelAdmin):
    list_display = ("type_name", "is_active", "created_at")
    search_fields = ("type_name",)
    list_filter = ("is_active",)


@admin.register(ItemMinMaxLevelMaster)
class ItemMinMaxLevelMasterAdmin(admin.ModelAdmin):
    list_display = ("type", "item_id", "min_qty", "max_qty", "reorder", "is_active", "created_at")
    search_fields = ("item_id",)
    list_filter = ("is_active", "type")


@admin.register(MainTaskCreationMaster)
class MainTaskCreationMasterAdmin(admin.ModelAdmin):
    list_display = ("main_task", "is_active", "created_at")
    search_fields = ("main_task",)
    list_filter = ("is_active",)


@admin.register(TaskCreationMaster)
class TaskCreationMasterAdmin(admin.ModelAdmin):
    list_display = ("task_name", "task_type", "is_active", "created_at")
    search_fields = ("task_name",)
    list_filter = ("is_active", "task_type")


@admin.register(GodownCreationMaster)
class GodownCreationMasterAdmin(admin.ModelAdmin):
    list_display = ("godown_name", "site_id", "is_active", "created_at")
    search_fields = ("godown_name",)
    list_filter = ("is_active",)


@admin.register(SupplierCreationMaster)
class SupplierCreationMasterAdmin(admin.ModelAdmin):
    list_display = ("supplier_code", "party_name", "party_type", "is_active", "created_at")
    search_fields = ("supplier_code", "party_name", "mobile_no")
    list_filter = ("is_active", "party_type", "supplier_category")


@admin.register(SupplierSupportingDocument)
class SupplierSupportingDocumentAdmin(admin.ModelAdmin):
    list_display = ("supplier", "doc_type", "created_at")
    search_fields = ("supplier__supplier_code",)
    list_filter = ("doc_type",)


@admin.register(RemarkSiteStoreCreationMaster)
class RemarkSiteStoreCreationMasterAdmin(admin.ModelAdmin):
    list_display = ("remark_type", "is_active", "created_at")
    search_fields = ("remark_type",)
    list_filter = ("is_active",)
