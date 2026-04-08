"""Cryptographic Primitives — ECDSA, commitments, Merkle trees, ECDH, AES-GCM."""

import hashlib
import hmac
import secrets
import logging
from dataclasses import dataclass
from typing import List, Optional, Tuple
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.backends import default_backend

logger = logging.getLogger(__name__)


@dataclass
class KeyPair:
    """An elliptic curve key pair (SECP256K1)."""
    private_key: ec.EllipticCurvePrivateKey
    public_key: ec.EllipticCurvePublicKey

    @classmethod
    def generate(cls) -> "KeyPair":
        private = ec.generate_private_key(ec.SECP256K1(), default_backend())
        return cls(private_key=private, public_key=private.public_key())

    @property
    def public_bytes(self) -> bytes:
        return self.public_key.public_bytes(
            serialization.Encoding.X962,
            serialization.PublicFormat.CompressedPoint,
        )

    @property
    def private_bytes(self) -> bytes:
        return self.private_key.private_numbers().private_value.to_bytes(32, "big")

    def sign(self, message: bytes) -> bytes:
        return self.private_key.sign(message, ec.ECDSA(hashes.SHA256()))

    def verify(self, message: bytes, signature: bytes) -> bool:
        try:
            self.public_key.verify(signature, message, ec.ECDSA(hashes.SHA256()))
            return True
        except Exception:
            return False


def hash_commitment(value: bytes, blinding: Optional[bytes] = None) -> Tuple[bytes, bytes]:
    """C = H(value || blinding). Returns (commitment, blinding)."""
    if blinding is None:
        blinding = secrets.token_bytes(32)
    commitment = hashlib.sha256(value + blinding).digest()
    return commitment, blinding


def verify_commitment(value: bytes, blinding: bytes, commitment: bytes) -> bool:
    expected = hashlib.sha256(value + blinding).digest()
    return hmac.compare_digest(expected, commitment)


def merkle_root(leaves: List[bytes]) -> bytes:
    if not leaves:
        return hashlib.sha256(b"empty").digest()
    if len(leaves) == 1:
        return leaves[0]
    layer = list(leaves)
    if len(layer) % 2 == 1:
        layer.append(layer[-1])
    while len(layer) > 1:
        next_layer = []
        for i in range(0, len(layer), 2):
            combined = hashlib.sha256(layer[i] + layer[i + 1]).digest()
            next_layer.append(combined)
        layer = next_layer
        if len(layer) > 1 and len(layer) % 2 == 1:
            layer.append(layer[-1])
    return layer[0]


def derive_shared_secret(private_key: ec.EllipticCurvePrivateKey,
                          peer_public_key: ec.EllipticCurvePublicKey) -> bytes:
    shared_key = private_key.exchange(ec.ECDH(), peer_public_key)
    return HKDF(algorithm=hashes.SHA256(), length=32, salt=None,
                info=b"singularion-nexus-v1").derive(shared_key)


def encrypt_message(key: bytes, plaintext: bytes, aad: bytes = b"") -> bytes:
    """AES-256-GCM encrypt. Returns nonce(12) + ciphertext."""
    nonce = secrets.token_bytes(12)
    return nonce + AESGCM(key).encrypt(nonce, plaintext, aad)


def decrypt_message(key: bytes, ciphertext: bytes, aad: bytes = b"") -> bytes:
    """AES-256-GCM decrypt. Input = nonce(12) + ciphertext."""
    return AESGCM(key).decrypt(ciphertext[:12], ciphertext[12:], aad)


def generate_did(public_key_bytes: bytes) -> str:
    key_hash = hashlib.sha256(public_key_bytes).hexdigest()[:40]
    return f"did:nexus:{key_hash}"
