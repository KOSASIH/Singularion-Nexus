"""Tests for cryptographic primitives."""
import pytest
from src.core.crypto import (
    KeyPair, hash_commitment, verify_commitment, merkle_root,
    derive_shared_secret, encrypt_message, decrypt_message, generate_did)

def test_keypair_generation():
    kp = KeyPair.generate()
    assert len(kp.public_bytes) == 33  # compressed point
    assert len(kp.private_bytes) == 32

def test_sign_verify():
    kp = KeyPair.generate()
    msg = b"hello singularion"
    sig = kp.sign(msg)
    assert kp.verify(msg, sig) is True
    assert kp.verify(b"wrong", sig) is False

def test_commitment():
    value = b"secret_value"
    commitment, blinding = hash_commitment(value)
    assert verify_commitment(value, blinding, commitment) is True
    assert verify_commitment(b"wrong", blinding, commitment) is False

def test_merkle_root():
    import hashlib
    leaves = [hashlib.sha256(f"leaf{i}".encode()).digest() for i in range(4)]
    root = merkle_root(leaves)
    assert len(root) == 32
    # Same leaves = same root
    root2 = merkle_root(leaves)
    assert root == root2
    # Different leaves = different root
    leaves2 = [hashlib.sha256(f"other{i}".encode()).digest() for i in range(4)]
    assert merkle_root(leaves2) != root

def test_merkle_root_single():
    import hashlib
    leaf = [hashlib.sha256(b"single").digest()]
    assert merkle_root(leaf) == leaf[0]

def test_ecdh_shared_secret():
    kp1 = KeyPair.generate()
    kp2 = KeyPair.generate()
    s1 = derive_shared_secret(kp1.private_key, kp2.public_key)
    s2 = derive_shared_secret(kp2.private_key, kp1.public_key)
    assert s1 == s2
    assert len(s1) == 32

def test_encrypt_decrypt():
    import secrets
    key = secrets.token_bytes(32)
    plaintext = b"sensitive transaction data"
    ct = encrypt_message(key, plaintext)
    decrypted = decrypt_message(key, ct)
    assert decrypted == plaintext

def test_encrypt_with_aad():
    import secrets
    key = secrets.token_bytes(32)
    aad = b"contract-id-123"
    pt = b"payment data"
    ct = encrypt_message(key, pt, aad)
    assert decrypt_message(key, ct, aad) == pt

def test_did_generation():
    kp = KeyPair.generate()
    did = generate_did(kp.public_bytes)
    assert did.startswith("did:nexus:")
    assert len(did) > 20
