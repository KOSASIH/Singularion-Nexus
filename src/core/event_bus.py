"""Event Bus — Async event-driven architecture for Nexus components."""

import asyncio
import logging
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Callable, Coroutine, Dict, List, Optional, Set
from datetime import datetime, timezone
from enum import Enum

logger = logging.getLogger(__name__)


class EventType(Enum):
    PEER_CONNECTED = "peer_connected"
    PEER_DISCONNECTED = "peer_disconnected"
    MESSAGE_RECEIVED = "message_received"
    MESSAGE_SENT = "message_sent"
    INTENT_SUBMITTED = "intent_submitted"
    INTENT_ROUTED = "intent_routed"
    INTENT_FULFILLED = "intent_fulfilled"
    INTENT_FAILED = "intent_failed"
    CONTRACT_CREATED = "contract_created"
    CONTRACT_PROPOSED = "contract_proposed"
    CONTRACT_ACCEPTED = "contract_accepted"
    CONTRACT_SETTLED = "contract_settled"
    CONTRACT_DISPUTED = "contract_disputed"
    CLUSTER_FORMED = "cluster_formed"
    CLUSTER_DISSOLVED = "cluster_dissolved"
    NEGOTIATION_STARTED = "negotiation_started"
    NEGOTIATION_ROUND = "negotiation_round"
    NEGOTIATION_SETTLED = "negotiation_settled"
    DEVICE_REGISTERED = "device_registered"
    BIOMETRIC_AUTH = "biometric_auth"
    INVISIBLE_TRANSACTION = "invisible_transaction"
    BLOCK_CREATED = "block_created"
    TRANSACTION_CONFIRMED = "transaction_confirmed"
    NODE_STARTED = "node_started"
    NODE_STOPPED = "node_stopped"
    HEALTH_CHECK = "health_check"


@dataclass
class Event:
    event_type: EventType
    source: str
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    event_id: str = ""

    def __post_init__(self):
        if not self.event_id:
            import hashlib
            content = f"{self.event_type.value}:{self.source}:{self.timestamp.isoformat()}"
            self.event_id = hashlib.sha256(content.encode()).hexdigest()[:16]


EventHandler = Callable[[Event], Coroutine[Any, Any, None]]


class EventBus:
    """Async event bus for decoupled component communication."""

    def __init__(self, max_queue_size: int = 10000):
        self._handlers: Dict[EventType, List[EventHandler]] = defaultdict(list)
        self._global_handlers: List[EventHandler] = []
        self._queue: asyncio.Queue = asyncio.Queue(maxsize=max_queue_size)
        self._running = False
        self._processed_count = 0
        self._error_count = 0

    def subscribe(self, event_type: EventType, handler: EventHandler) -> None:
        self._handlers[event_type].append(handler)

    def subscribe_all(self, handler: EventHandler) -> None:
        self._global_handlers.append(handler)

    def unsubscribe(self, event_type: EventType, handler: EventHandler) -> None:
        if handler in self._handlers[event_type]:
            self._handlers[event_type].remove(handler)

    async def publish(self, event: Event) -> None:
        if self._running:
            await self._queue.put(event)
        else:
            await self._dispatch(event)

    async def start(self) -> None:
        self._running = True
        asyncio.create_task(self._process_loop())

    async def stop(self) -> None:
        self._running = False

    async def _process_loop(self) -> None:
        while self._running:
            try:
                event = await asyncio.wait_for(self._queue.get(), timeout=1.0)
                await self._dispatch(event)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self._error_count += 1

    async def _dispatch(self, event: Event) -> None:
        handlers = list(self._handlers.get(event.event_type, []))
        handlers.extend(self._global_handlers)
        for handler in handlers:
            try:
                await handler(event)
            except Exception as e:
                self._error_count += 1
        self._processed_count += 1

    @property
    def stats(self) -> Dict[str, Any]:
        return {
            "processed": self._processed_count,
            "errors": self._error_count,
            "queue_size": self._queue.qsize(),
            "handler_count": sum(len(h) for h in self._handlers.values()) + len(self._global_handlers),
        }
