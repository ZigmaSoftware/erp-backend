import uuid


def generate_unique_id():
    """Return a short, unique, ASCII-safe token for master IDs."""
    return uuid.uuid4().hex[:8].upper()
