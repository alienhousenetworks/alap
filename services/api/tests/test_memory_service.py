from cryptography.fernet import Fernet
from app.services import memory


def test_memory_encryption_round_trip(monkeypatch):
    key = Fernet.generate_key().decode("ascii")
    monkeypatch.setattr(memory.settings, "memory_encryption_key", key)
    encrypted = memory.encrypt_memory("The user prefers concise replies.")
    assert encrypted != "The user prefers concise replies."
    assert memory.decrypt_memory(encrypted) == "The user prefers concise replies."


def test_memory_fingerprint_normalizes_whitespace_and_case():
    assert memory._fingerprint("  Likes   science fiction ") == memory._fingerprint("likes science fiction")
