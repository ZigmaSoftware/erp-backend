import random
import time
from datetime import datetime

MAX_ATTEMPTS = 5


def generate_random_no(model_class, field_name="random_no", length=5):
    """
    random_no: a random n-digit number (default 5 digits), unique per model_class.

    Mirrors the legacy PHP generator:
        $random_no = rand(00000, 99999);
    """
    max_value = (10 ** length) - 1

    for _ in range(MAX_ATTEMPTS):
        code = str(random.randint(0, max_value)).zfill(length)
        if not model_class.objects.filter(**{field_name: code}).exists():
            return code

    raise RuntimeError(f"Unable to generate a unique {field_name} after {MAX_ATTEMPTS} attempts.")


def generate_random_sc(model_class, field_name="random_sc"):
    """
    random_sc: current timestamp as ddmmyyhhmmss (12 digits), unique per model_class.

    Mirrors the legacy PHP generator:
        $random_sc = date('dmyhis');
    """
    for _ in range(MAX_ATTEMPTS):
        code = datetime.now().strftime("%d%m%y%I%M%S")
        if not model_class.objects.filter(**{field_name: code}).exists():
            return code
        time.sleep(1)

    raise RuntimeError(f"Unable to generate a unique {field_name} after {MAX_ATTEMPTS} attempts.")
