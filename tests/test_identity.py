"""Tests for DID identity system."""
import pytest
from src.core.crypto import KeyPair
from src.core.identity import IdentityRegistry

@pytest.fixture
def registry():
    return IdentityRegistry()

def test_create_identity(registry):
    kp = KeyPair.generate()
    doc = registry.create_identity(kp)
    assert doc.did.startswith("did:nexus:")
    assert registry.identity_count == 1

def test_resolve_identity(registry):
    kp = KeyPair.generate()
    doc = registry.create_identity(kp)
    resolved = registry.resolve(doc.did)
    assert resolved is not None
    assert resolved.did == doc.did

def test_issue_and_verify_credential(registry):
    issuer_kp = KeyPair.generate()
    subject_kp = KeyPair.generate()
    issuer_doc = registry.create_identity(issuer_kp)
    subject_doc = registry.create_identity(subject_kp)
    cred = registry.issue_credential(
        issuer_kp, issuer_doc.did, subject_doc.did,
        "MeshTrust", {"level": "gold"})
    assert cred is not None
    assert cred.credential_type == "MeshTrust"
    assert registry.verify_credential(cred) is True

def test_revoke_credential(registry):
    ik = KeyPair.generate()
    sk = KeyPair.generate()
    id_ = registry.create_identity(ik)
    sd = registry.create_identity(sk)
    cred = registry.issue_credential(ik, id_.did, sd.did, "Test", {"x": 1})
    registry.revoke_credential(cred.credential_id)
    assert registry.verify_credential(cred) is False

def test_did_document_to_dict(registry):
    kp = KeyPair.generate()
    doc = registry.create_identity(kp, service_endpoints={"mesh": "tcp://localhost:9090"})
    d = doc.to_dict()
    assert d["@context"] == "https://www.w3.org/ns/did/v1"
    assert len(d["service"]) == 1
