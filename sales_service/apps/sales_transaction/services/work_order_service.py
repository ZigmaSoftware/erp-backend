from django.db import transaction

from apps.sales_transaction.models.work_order import WorkOrderMain, WorkOrderSub
from apps.sales_shared.services.number_generation import generate_work_order_number


class WorkOrderService:

    @staticmethod
    def create_work_order(data, sub_items_data, user_id=""):
        with transaction.atomic():
            work_order_no = generate_work_order_number(
                site_code=data.get("site_code", "HO")
            )
            work_order = WorkOrderMain.objects.create(
                workorderno=work_order_no,
                suppliername=data["suppliername"],
                site_id=data["site_id"],
                plant_name=data.get("plant_name", ""),
                department_name=data.get("department_name", ""),
                description=data.get("description", ""),
                entry_date=data["entry_date"],
                work_type=data.get("work_type", ""),
                payment_terms=data.get("payment_terms", ""),
                comp_period=data.get("comp_period", ""),
                tds=data.get("tds", 0),
                package_forward=data.get("package_forward", 0),
                transport_cost=data.get("transport_cost", 0),
                freight_charge=data.get("freight_charge", 0),
                budget_no=data.get("budget_no", ""),
                budget_entry_no=data.get("budget_entry_no", ""),
                budget_po_type=data.get("budget_po_type", ""),
                staff_id=user_id,
                created_by=user_id,
                updated_by=user_id,
            )

            total_amount = 0
            total_qty = 0
            for item in sub_items_data:
                amt = item.get("qty", 0) * item.get("rate", 0)
                tax_amt = (amt / 100) * item.get("tax_per", 0) if item.get("tax_per") else 0
                WorkOrderSub.objects.create(
                    work_order=work_order,
                    workorderno=work_order_no,
                    entry_date=work_order.entry_date,
                    suppliername=data["suppliername"],
                    site_id=data["site_id"],
                    description_one=item.get("description", ""),
                    itemname=item.get("itemname", ""),
                    qty=item.get("qty", 0),
                    unit_id=item.get("unit_id", ""),
                    rate=item.get("rate", 0),
                    amount=amt,
                    tax_per=item.get("tax_per", 0),
                    tot_tax_amnt=tax_amt,
                    plant_name=data.get("plant_name", ""),
                    work_type=data.get("work_type", ""),
                    staff_id=user_id,
                    budget_no=item.get("budget_no", ""),
                    type=item.get("type", ""),
                )
                total_amount += amt
                total_qty += item.get("qty", 0)

            work_order.tot_amount = total_amount
            work_order.net_amt = total_amount
            work_order.tot_qty = total_qty
            work_order.save(update_fields=["tot_amount", "net_amt", "tot_qty"])
            return work_order

    @staticmethod
    def update_work_order(unique_id, data, sub_items_data, user_id=""):
        with transaction.atomic():
            wo = WorkOrderMain.objects.select_for_update().get(
                unique_id=unique_id, is_deleted=False
            )
            for field in [
                "suppliername", "site_id", "plant_name", "department_name",
                "description", "work_type", "payment_terms", "comp_period",
                "tds", "package_forward", "transport_cost", "freight_charge",
                "budget_no", "budget_entry_no", "budget_po_type",
            ]:
                if field in data:
                    setattr(wo, field, data[field])
            wo.updated_by = user_id
            wo.save()

            if sub_items_data is not None:
                wo.sub_items.filter(is_deleted=False).update(is_deleted=True, is_active=False)
                total_amount = 0
                total_qty = 0
                for item in sub_items_data:
                    amt = item.get("qty", 0) * item.get("rate", 0)
                    WorkOrderSub.objects.create(
                        work_order=wo, workorderno=wo.workorderno,
                        entry_date=wo.entry_date, suppliername=wo.suppliername,
                        site_id=wo.site_id,
                        description_one=item.get("description", ""),
                        itemname=item.get("itemname", ""),
                        qty=item.get("qty", 0), unit_id=item.get("unit_id", ""),
                        rate=item.get("rate", 0), amount=amt,
                        tax_per=item.get("tax_per", 0),
                        plant_name=wo.plant_name, work_type=wo.work_type,
                        staff_id=user_id, budget_no=item.get("budget_no", ""),
                    )
                    total_amount += amt
                    total_qty += item.get("qty", 0)
                wo.tot_amount = total_amount
                wo.net_amt = total_amount
                wo.tot_qty = total_qty
                wo.save(update_fields=["tot_amount", "net_amt", "tot_qty"])
                wo.reset_approvals()

            return wo
