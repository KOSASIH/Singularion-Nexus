"""Nexus Core — Orchestrator, event bus, crypto, identity, reputation, resilience."""

from .orchestrator import NexusOrchestrator, NexusConfig, Intent
from .event_bus import EventBus, Event, EventType
from .crypto import KeyPair, hash_commitment, verify_commitment, merkle_root, generate_did
from .identity import IdentityRegistry, DIDDocument, VerifiableCredential
from .reputation import ReputationEngine, ReputationEvent, ReputationProfile
from .resilience import CircuitBreaker, TokenBucketRateLimiter, CircuitBreakerOpenError

__all__ = [
    "NexusOrchestrator", "NexusConfig", "Intent",
    "EventBus", "Event", "EventType",
    "KeyPair", "hash_commitment", "verify_commitment", "merkle_root", "generate_did",
    "IdentityRegistry", "DIDDocument", "VerifiableCredential",
    "ReputationEngine", "ReputationEvent", "ReputationProfile",
    "CircuitBreaker", "TokenBucketRateLimiter", "CircuitBreakerOpenError",
]
