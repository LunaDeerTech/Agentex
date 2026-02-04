"""Encryption utilities for sensitive data like API keys."""

import base64
import os

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from app.core.config import get_settings


def _derive_key(secret: str, salt: bytes) -> bytes:
    """Derive a Fernet-compatible key from secret and salt."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(secret.encode()))
    return key


def encrypt_api_key(api_key: str) -> str:
    """
    Encrypt an API key for secure storage.

    Args:
        api_key: The plaintext API key to encrypt

    Returns:
        Base64-encoded encrypted string with salt prefix
    """
    settings = get_settings()
    salt = os.urandom(16)
    key = _derive_key(settings.SECRET_KEY, salt)
    fernet = Fernet(key)
    encrypted = fernet.encrypt(api_key.encode())
    # Combine salt and encrypted data
    combined = base64.urlsafe_b64encode(salt + encrypted)
    return combined.decode()


def decrypt_api_key(encrypted_key: str) -> str:
    """
    Decrypt an encrypted API key.

    Args:
        encrypted_key: The encrypted API key string

    Returns:
        The decrypted plaintext API key

    Raises:
        ValueError: If decryption fails
    """
    settings = get_settings()
    try:
        combined = base64.urlsafe_b64decode(encrypted_key.encode())
        salt = combined[:16]
        encrypted = combined[16:]
        key = _derive_key(settings.SECRET_KEY, salt)
        fernet = Fernet(key)
        decrypted = fernet.decrypt(encrypted)
        return decrypted.decode()
    except Exception as e:
        raise ValueError(f"Failed to decrypt API key: {e}") from e


def mask_api_key(api_key: str, visible_chars: int = 4) -> str:
    """
    Mask an API key for display, showing only first and last few characters.

    Args:
        api_key: The API key to mask
        visible_chars: Number of characters to show at start and end

    Returns:
        Masked API key string (e.g., "sk-a***xyz")
    """
    if len(api_key) <= visible_chars * 2:
        return "*" * len(api_key)
    return f"{api_key[:visible_chars]}***{api_key[-visible_chars:]}"
