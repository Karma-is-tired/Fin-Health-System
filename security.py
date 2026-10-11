"""Password hashing and login tokens (no web framework needed here)."""
import hashlib
import hmac
import logging
import os
import secrets
from datetime import datetime, timedelta, timezone

import jwt

logger = logging.getLogger("finhealth")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("TOKEN_MINUTES", "1440"))
PBKDF2_ITERATIONS = int(os.environ.get("PBKDF2_ITERATIONS", "600000"))

SECRET_KEY = os.environ.get("SECRET_KEY")
if not SECRET_KEY:
    # The server still starts, but everyone is signed out on every restart.
    SECRET_KEY = secrets.token_urlsafe(48)
    logger.warning(
        "SECRET_KEY is not set, so a temporary key is being used. "
        "Set SECRET_KEY in your hosting settings."
    )

PREFIX = "pbkdf2_sha256"


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS
    )
    return f"{PREFIX}${PBKDF2_ITERATIONS}${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    if stored.startswith(PREFIX + "$"):
        try:
            _, iterations, salt_hex, hash_hex = stored.split("$")
            digest = hashlib.pbkdf2_hmac(
                "sha256",
                password.encode("utf-8"),
                bytes.fromhex(salt_hex),
                int(iterations),
            )
        except ValueError:
            return False
        return hmac.compare_digest(digest.hex(), hash_hex)
    # Accounts made before this upgrade used a plain, unsalted SHA-256 hash.
    legacy = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return hmac.compare_digest(legacy, stored)


def needs_rehash(stored: str) -> bool:
    return not stored.startswith(PREFIX + "$")


def create_token(email: str) -> str:
    expires = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub": email, "exp": expires}, SECRET_KEY, algorithm=ALGORITHM)


def read_token(token: str):
    """Returns the email inside a valid token, or None."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        return None
    sub = payload.get("sub")
    return sub if isinstance(sub, str) else None
