from datetime import datetime

from django.db import transaction


def generate_target_entry_no(model_class, field_name="target_no", prefix="TAR", sequence_length=4):
    """
    Generates a sequential, month-scoped target entry number, e.g.:
        TAR-2607-0001, TAR-2607-0002, ... (resets for each new yymm prefix)
    """
    month_prefix = f"{prefix}-{datetime.now().strftime('%y%m')}-"

    with transaction.atomic():
        last_record = (
            model_class.objects
            .select_for_update()
            .filter(**{f"{field_name}__startswith": month_prefix})
            .order_by("-id")
            .first()
        )

        last_number = 0
        if last_record:
            existing_value = getattr(last_record, field_name) or ""
            try:
                last_number = int(existing_value.replace(month_prefix, ""))
            except ValueError:
                last_number = 0

        new_number = str(last_number + 1).zfill(sequence_length)
        return f"{month_prefix}{new_number}"
