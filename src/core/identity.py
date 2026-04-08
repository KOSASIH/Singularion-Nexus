"""Decentralized Identity (DID) System for PEA agents."""

import hashlib
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

from .crypto import KeyPair, generate_did

logger = logging.getLogger(__name__)


@dataclass
class VerifiableCredential:
    credential_id: str
    issuer_did: str
    subject_did: str
    credential_type: str
    claims: Dict[str, Any]
    issued_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None
    signature: bytes = b""
    revoked: bool = False

    @property
    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return datetime.now(timezone.utc) > self.expires_at


@dataclass
class DIDDocument:
    did: str
    public_key: bytes
    authentication: List[str] = field(default_factory=list)
    service_endpoints: Dict[str, str] = field(default_factory=dict)
    credentials: List[VerifiableCredential] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "@context": "https://www.w3.org/ns/did/v1",
            "id": self.did,
            "publicKey": self.public_key.hex(),
            "authentication": self.authentication,
            "service": [
                {"id": f"{self.did}#{k}", "type": k, "serviceEndpoint": v}
                for k, v in self.service_endpoints.items()
            ],
        }


class IdentityRegistry:
    def __init__(self):
        self._documents: Dict[str, DIDDocument] = {}
        self._revoked_credentials: set = set()

    def create_identity(self, key_pair: KeyPair,
                       service_endpoints: Optional[Dict[str, str]] = None) -> DIDDocument:
        did = generate_did(key_pair.public_bytes)
        doc = DIDDocument(
            did=did, public_key=key_pair.public_bytes,
            authentication=[f"{did}#key-1"],
            service_endpoints=service_endpoints or {},
        )
        self._documents[did] = doc
        return doc

    def resolve(self, did: str) -> Optional[DIDDocument]:
        return self._documents.get(did)

    def issue_credential(self, issuer_key: KeyPair, issuer_did: str,
                        subject_did: str, credential_type: str,
                        claims: Dict[str, Any]) -> Optional[VerifiableCredential]:
        if issuer_did not in self._documents or subject_did not in self._documents:
            return None
        cred_id = hashlib.sha256(
            f"{issuer_did}:{subject_did}:{credential_type}:{datetime.now(timezone.utc).timestamp()}".encode()
        ).hexdigest()[:16]
        cred_data = f"{cred_id}:{issuer_did}:{subject_did}:{credential_type}".encode()
        signature = issuer_key.sign(cred_data)
        cred = VerifiableCredential(
            credential_id=cred_id, issuer_did=issuer_did, subject_did=subject_did,
            credential_type=credential_type, claims=claims, signature=signature,
        )
        self._documents[subject_did].credentials.append(cred)
        return cred

    def verify_credential(self, credential: VerifiableCredential) -> bool:
        if credential.credential_id in self._revoked_credentials or credential.is_expired:
            return False
        issuer_doc = self._documents.get(credential.issuer_did)
        if not issuer_doc:
            return False
        from cryptography.hazmat.primitives.asymmetric import ec
        from cryptography.hazmat.primitives import hashes
        try:
            pub_key = ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP256K1(), issuer_doc.public_key)
            cred_data = f"{credential.credential_id}:{credential.issuer_did}:{credential.subject_did}:{credential.credential_type}".encode()
            pub_key.verify(credential.signature, cred_data, ec.ECDSA(hashes.SHA256()))
            return True
        except Exception:
            return False

    def revoke_credential(self, credential_id: str) -> bool:
        self._revoked_credentials.add(credential_id)
        return True

    @property
    def identity_count(self) -> int:
        return len(self._documents)
