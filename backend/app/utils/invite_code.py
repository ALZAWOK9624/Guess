"""Invite code generation utilities.

Generates 8-character alphanumeric codes, excluding visually ambiguous
characters (O, 0, I, 1) for readability.
"""

import secrets
import string

# Exclude O/0/I/1 to avoid confusion
_ALPHABET = (
    string.ascii_uppercase.replace("O", "").replace("I", "")
    + string.digits.replace("0", "").replace("1", "")
)

CODE_LENGTH = 8
MAX_RETRIES = 10


def generate_invite_code() -> str:
    """Generate a random 8-character invite code.

    Uses secrets.choice for cryptographic randomness.
    Characters: A-Z (minus O, I) + 2-9 (minus 0, 1).
    """
    return "".join(secrets.choice(_ALPHABET) for _ in range(CODE_LENGTH))
