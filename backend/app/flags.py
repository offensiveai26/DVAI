"""Flag generator - produces deterministic flags from a secret key so flags never appear in source code."""

import hashlib
import hmac
import os

_SECRET = os.getenv("DVAI_FLAG_SECRET", "dvai-default-secret-change-me-in-prod")


def get_flag(challenge_id: str) -> str:
    """Generate a deterministic flag for a challenge ID."""
    h = hmac.new(_SECRET.encode(), challenge_id.encode(), hashlib.sha256).hexdigest()[:16]
    return f"DVAI{{{h}}}"
