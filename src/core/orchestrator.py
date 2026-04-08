"""Nexus Core Orchestrator — Enhanced with event bus, identity, reputation."""

import asyncio
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

from .event_bus import EventBus, Event, EventType
from .identity import IdentityRegistry
from .reputation import ReputationEngine
from .resilience import CircuitBreaker, TokenBucketRateLimiter

logger = logging.getLogger(__name__)


@dataclass
class NexusConfig:
    node_id: str = ""
    mesh_port: int = 9090
    api_port: int = 8080
    max_peers: int = 256
    quantum_backend: str = "simulator"
    zkp_proving_system: str = "groth16"
    enable_collective_bargaining: bool = True
    enable_iot_gateway: bool = True
    log_level: str = "INFO"
    rate_limit_rps: float = 1000.0
    circuit_breaker_threshold: int = 10


@dataclass
class Intent:
    intent_id: str
    pea_id: str
    intent_type: str
    domain: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    constraints: Dict[str, Any] = field(default_factory=dict)
    priority: int = 5
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = "pending"
    fulfillment_result: Optional[Dict[str, Any]] = None


class NexusOrchestrator:
    def __init__(self, config: NexusConfig):
        self.config = config
        self.active_intents: Dict[str, Intent] = {}
        self.peer_registry: Dict[str, Any] = {}
        self._running = False
        self.event_bus = EventBus()
        self.identity_registry = IdentityRegistry()
        self.reputation_engine = ReputationEngine()
        self.rate_limiter = TokenBucketRateLimiter(
            rate=config.rate_limit_rps, capacity=int(config.rate_limit_rps * 2))
        self.circuit_breaker = CircuitBreaker(
            name="nexus-main", failure_threshold=config.circuit_breaker_threshold)
        self._intent_count = 0
        logger.info(f"NexusOrchestrator initialized — node_id={config.node_id}")

    async def start(self) -> None:
        self._running = True
        await self.event_bus.start()
        await self.event_bus.publish(Event(
            event_type=EventType.NODE_STARTED, source=self.config.node_id,
            data={"mesh_port": self.config.mesh_port, "api_port": self.config.api_port}))
        logger.info("Singularion Nexus orchestrator is running.")

    async def stop(self) -> None:
        self._running = False
        await self.event_bus.publish(Event(event_type=EventType.NODE_STOPPED, source=self.config.node_id))
        await self.event_bus.stop()

    async def submit_intent(self, intent: Intent) -> str:
        if not await self.rate_limiter.acquire():
            intent.status = "rate_limited"
            return f"rate_limited:{intent.intent_id}"
        self.active_intents[intent.intent_id] = intent
        self._intent_count += 1
        await self.event_bus.publish(Event(
            event_type=EventType.INTENT_SUBMITTED, source=self.config.node_id,
            data={"intent_id": intent.intent_id, "domain": intent.domain}))
        return await self._route_intent(intent)

    async def register_peer(self, peer_id: str, peer_info: Dict[str, Any]) -> bool:
        if len(self.peer_registry) >= self.config.max_peers:
            return False
        self.peer_registry[peer_id] = {
            **peer_info, "connected_at": datetime.now(timezone.utc), "status": "active"}
        await self.event_bus.publish(Event(
            event_type=EventType.PEER_CONNECTED, source=self.config.node_id,
            data={"peer_id": peer_id}))
        return True

    async def _route_intent(self, intent: Intent) -> str:
        intent.status = "routing"
        await self.event_bus.publish(Event(
            event_type=EventType.INTENT_ROUTED, source=self.config.node_id,
            data={"intent_id": intent.intent_id}))
        return f"routed:{intent.intent_id}"

    @property
    def stats(self) -> Dict[str, Any]:
        return {
            "node_id": self.config.node_id, "running": self._running,
            "peers": len(self.peer_registry), "active_intents": len(self.active_intents),
            "total_intents": self._intent_count,
            "identities": self.identity_registry.identity_count,
            "event_bus": self.event_bus.stats}
