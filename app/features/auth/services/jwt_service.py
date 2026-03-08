"""JWT authentication service for admin access."""
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt

JWT_SECRET: str = os.getenv(
    "JWT_SECRET", "change-me-in-production-kings-gambit-secret"
)
JWT_ALGORITHM: str = "HS256"
JWT_EXPIRY_HOURS: int = 24


def create_access_token(username: str) -> str:
    """Create a signed JWT for the given admin username."""
    now = datetime.now(timezone.utc)
    payload: dict = {
        "sub": username,
        "iat": now,
        "exp": now + timedelta(hours=JWT_EXPIRY_HOURS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_token(token: str) -> Optional[dict]:
    """Decode and verify a JWT. Returns payload dict or None."""
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
