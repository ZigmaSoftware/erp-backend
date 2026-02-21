import string
from django.db import transaction
from django.utils.crypto import get_random_string


def generate_vehicle_request_no(model_class, prefix="REQ_", sequence_length=5, random_length=5):
    """
    Generates unique request number like:
    REQ_00001A9K2X

    Args:
        model_class: VehicleRequest model class
        prefix: Prefix for ID
        sequence_length: Length of numeric sequence
        random_length: Length of random alphanumeric string

    Returns:
        Unique request number string
    """

    with transaction.atomic():

        last_record = (
            model_class.objects
            .select_for_update()
            .order_by("-id")
            .first()
        )

        if last_record and last_record.request_no:
            try:
                last_number = int(
                    last_record.request_no
                    .replace(prefix, "")[:sequence_length]
                )
            except (ValueError, IndexError):
                last_number = 0
        else:
            last_number = 0

        new_number = str(last_number + 1).zfill(sequence_length)

        random_part = get_random_string(
            random_length,
            allowed_chars=string.ascii_uppercase + string.digits
        )

        request_no = f"{prefix}{new_number}{random_part}"

        return request_no
