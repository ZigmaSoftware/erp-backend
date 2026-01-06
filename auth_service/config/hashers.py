from django.contrib.auth.hashers import PBKDF2PasswordHasher


class PBKDF2SHA256IterationsHasher(PBKDF2PasswordHasher):
    """Explicit PBKDF2 SHA256 hasher with a fixed iteration count.

    Using an explicit hasher avoids relying on a global setting name and
    guarantees new passwords will be hashed with 120000 iterations.
    """

    algorithm = "pbkdf2_sha256"
    iterations = 120000
