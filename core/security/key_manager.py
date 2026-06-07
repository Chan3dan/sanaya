"""Encrypted key management backed by OS keychain and the database."""

from pathlib import Path

from cryptography.fernet import Fernet
import keyring
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.db.models import ApiKey


class KeyManager:
    """Manages Fernet encryption keys and encrypted provider API keys."""

    service_name = "SanayaAIOS"
    master_key_name = "fernet_master_key"

    def __init__(self) -> None:
        """Create a key manager and load or generate the master key."""
        key = keyring.get_password(self.service_name, self.master_key_name)
        if key is None:
            key = Fernet.generate_key().decode("utf-8")
            try:
                keyring.set_password(self.service_name, self.master_key_name, key)
            except Exception:
                key_path = Path("data/security/fernet.key")
                key_path.parent.mkdir(parents=True, exist_ok=True)
                if key_path.exists():
                    key = key_path.read_text(encoding="utf-8").strip()
                else:
                    key_path.write_text(key, encoding="utf-8")
        self._fernet = Fernet(key.encode("utf-8"))

    def encrypt_text(self, plaintext: str) -> str:
        """Encrypt plaintext for at-rest storage."""
        return self._fernet.encrypt(plaintext.encode("utf-8")).decode("utf-8")

    def decrypt_text(self, ciphertext: str) -> str:
        """Decrypt text into memory only."""
        return self._fernet.decrypt(ciphertext.encode("utf-8")).decode("utf-8")

    async def store_api_key(self, db: AsyncSession, provider: str, plaintext_key: str) -> None:
        """Encrypt and store a provider API key."""
        encrypted = self.encrypt_text(plaintext_key)
        existing = await db.get(ApiKey, provider)
        if existing:
            existing.key_enc = encrypted
        else:
            db.add(ApiKey(provider=provider, key_enc=encrypted))
        await db.commit()

    async def get_api_key(self, db: AsyncSession, provider: str) -> str | None:
        """Return a decrypted provider API key if configured."""
        row = await db.scalar(select(ApiKey).where(ApiKey.provider == provider))
        return self.decrypt_text(row.key_enc) if row else None

    async def delete_api_key(self, db: AsyncSession, provider: str) -> None:
        """Delete a provider API key."""
        row = await db.get(ApiKey, provider)
        if row:
            await db.delete(row)
            await db.commit()
