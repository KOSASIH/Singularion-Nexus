"""PEA Mesh Protocol implementation.

Handles peer discovery, connection management, and message routing
across the decentralized PEA mesh network.
"""

import asyncio
import hashlib
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class MessageType(Enum):
    PEER_DISCOVERY = "peer_discovery"
    INTENT_BROADCAST = "intent_broadcast"
    CONTRACT_PROPOSAL = "contract_proposal"
    CONTRACT_ACCEPT = "contract_accept"
    CLUSTER_JOIN = "cluster_join"
    CLUSTER_LEAVE = "cluster_leave"
    HEARTBEAT = "heartbeat"
    STATE_SYNC = "state_sync"


@dataclass
class PeerInfo:
    peer_id: str
    address: str
    port: int
    capabilities: Set[str] = field(default_factory=set)
    reputation_score: float = 1.0
    connected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_heartbeat: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class MeshMessage:
    message_id: str
    message_type: MessageType
    sender_id: str
    payload: Dict[str, Any]
    ttl: int = 10
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def hash(self) -> str:
        content = f"{self.message_id}:{self.sender_id}:{self.timestamp.isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()


class MeshProtocol:
    """PEA Mesh Protocol - manages peer connections and message routing."""

    def __init__(self, node_id: str, listen_port: int = 9090):
        self.node_id = node_id
        self.listen_port = listen_port
        self.peers: Dict[str, PeerInfo] = {}
        self.seen_messages: Set[str] = set()
        self._message_handlers: Dict[MessageType, List[Callable]] = {}
        self._running = False

    async def start(self) -> None:
        self._running = True
        logger.info(f"Mesh protocol started on port {self.listen_port}")
        asyncio.create_task(self._heartbeat_loop())
        asyncio.create_task(self._peer_cleanup_loop())

    async def stop(self) -> None:
        self._running = False

    async def connect_peer(self, address: str, port: int) -> Optional[PeerInfo]:
        peer_id = hashlib.sha256(f"{address}:{port}".encode()).hexdigest()[:16]
        peer = PeerInfo(peer_id=peer_id, address=address, port=port)
        self.peers[peer_id] = peer
        logger.info(f"Connected to peer {peer_id} at {address}:{port}")
        return peer

    async def broadcast(self, message: MeshMessage) -> int:
        if message.hash in self.seen_messages:
            return 0
        self.seen_messages.add(message.hash)
        sent = 0
        for pid, peer in self.peers.items():
            if pid != message.sender_id:
                await self._send_to_peer(peer, message)
                sent += 1
        return sent

    def on_message(self, msg_type: MessageType, handler: Callable) -> None:
        self._message_handlers.setdefault(msg_type, []).append(handler)

    async def _send_to_peer(self, peer: PeerInfo, message: MeshMessage) -> bool:
        logger.debug(f"Sending {message.message_type.value} to {peer.peer_id}")
        return True

    async def _heartbeat_loop(self) -> None:
        while self._running:
            for peer in self.peers.values():
                hb = MeshMessage(
                    message_id=f"hb-{self.node_id}-{datetime.now(timezone.utc).timestamp()}",
                    message_type=MessageType.HEARTBEAT,
                    sender_id=self.node_id,
                    payload={"status": "alive"},
                )
                await self._send_to_peer(peer, hb)
            await asyncio.sleep(30)

    async def _peer_cleanup_loop(self) -> None:
        while self._running:
            now = datetime.now(timezone.utc)
            stale = [pid for pid, p in self.peers.items() if (now - p.last_heartbeat).total_seconds() > 120]
            for pid in stale:
                del self.peers[pid]
                logger.info(f"Removed stale peer: {pid}")
            await asyncio.sleep(60)
