from __future__ import annotations

import base64
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from src.core.config import settings
from src.core.logging import get_logger

logger = get_logger(__name__)

# ── Local dev key derivation (NOT for production) ─────────────────────────────
# In production, replace this with real KMS calls (AWS KMS, GCP KMS, etc.)

_LOCAL_KEY_CACHE: dict[str, bytes] = {}


def _get_or_derive_key(key_ref: str) -> bytes:
    """Derive a deterministic AES-256 key from key_ref (dev only)."""
    if key_ref not in _LOCAL_KEY_CACHE:
        import hashlib
        raw = hashlib.sha256(f"{settings.app_secret_key}:{key_ref}".encode()).digest()
        _LOCAL_KEY_CACHE[key_ref] = raw
    return _LOCAL_KEY_CACHE[key_ref]


# ── Public API ──────────────────────────────────────────────────────────────

def encrypt_secret(plaintext: str, key_ref: str | None = None) -> tuple[str, str]:
    """
    Encrypt a plaintext secret using AES-256-GCM.

    Returns (ciphertext_b64, kms_key_ref).
    In production swap _get_or_derive_key for a real KMS data-key call.
    """
    kms_ref = key_ref or settings.kms_key_ref
    key = _get_or_derive_key(kms_ref)
    nonce = os.urandom(12)
    aesgcm = AESGCM(key)
    ct = aesgcm.encrypt(nonce, plaintext.encode(), None)
    encoded = base64.b64encode(nonce + ct).decode()
    return encoded, kms_ref


def decrypt_secret(ciphertext_b64: str, key_ref: str) -> str:
    """Decrypt a secret previously encrypted with encrypt_secret."""
    key = _get_or_derive_key(key_ref)
    data = base64.b64decode(ciphertext_b64)
    nonce = data[:12]
    ct = data[12:]
    aesgcm = AESGCM(key)
    plaintext = aesgcm.decrypt(nonce, ct, None)
    return plaintext.decode()


def rotate_key(ciphertext_b64: str, old_key_ref: str, new_key_ref: str) -> tuple[str, str]:
    """Re-encrypt a secret under a new KMS key reference."""
    plaintext = decrypt_secret(ciphertext_b64, old_key_ref)
    return encrypt_secret(plaintext, new_key_ref)
