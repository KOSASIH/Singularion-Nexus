"""DAG-Based Distributed Ledger — Directed Acyclic Graph for settlement."""

import hashlib
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


@dataclass
class Transaction:
    txn_id: str
    sender: str
    receiver: str
    amount: float
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    signature: bytes = b""

    @property
    def hash(self) -> str:
        content = f"{self.txn_id}:{self.sender}:{self.receiver}:{self.amount}:{self.timestamp.isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()


@dataclass
class DAGNode:
    """A node in the DAG ledger."""
    node_id: str
    transactions: List[Transaction]
    parents: List[str]  # parent node IDs
    creator: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    weight: int = 1
    confirmed: bool = False

    @property
    def hash(self) -> str:
        txn_hashes = ":".join(t.hash for t in self.transactions)
        parent_str = ":".join(sorted(self.parents))
        content = f"{self.node_id}:{txn_hashes}:{parent_str}:{self.creator}:{self.timestamp.isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()

    @property
    def merkle_root(self) -> str:
        if not self.transactions:
            return hashlib.sha256(b"empty").hexdigest()
        leaves = [bytes.fromhex(t.hash) for t in self.transactions]
        layer = list(leaves)
        if len(layer) % 2 == 1:
            layer.append(layer[-1])
        while len(layer) > 1:
            next_l = []
            for i in range(0, len(layer), 2):
                next_l.append(hashlib.sha256(layer[i] + layer[i+1]).digest())
            layer = next_l
            if len(layer) > 1 and len(layer) % 2 == 1:
                layer.append(layer[-1])
        return layer[0].hex()


class DAGLedger:
    """DAG-based distributed ledger for transaction settlement."""

    def __init__(self, confirmation_threshold: int = 5):
        self.nodes: Dict[str, DAGNode] = {}
        self.tips: Set[str] = set()  # Current tip nodes (no children)
        self.genesis_id: Optional[str] = None
        self.confirmation_threshold = confirmation_threshold
        self._txn_index: Dict[str, str] = {}  # txn_id -> node_id

    def initialize(self, creator: str = "genesis") -> DAGNode:
        """Create the genesis node."""
        genesis = DAGNode(
            node_id="genesis", transactions=[], parents=[],
            creator=creator, confirmed=True, weight=self.confirmation_threshold)
        self.nodes["genesis"] = genesis
        self.tips.add("genesis")
        self.genesis_id = "genesis"
        return genesis

    def add_node(self, transactions: List[Transaction], creator: str,
                 parent_ids: Optional[List[str]] = None) -> Optional[DAGNode]:
        """Add a new node to the DAG."""
        if not self.nodes:
            return self.initialize(creator)

        parents = parent_ids or list(self.tips)[:2]
        if not parents:
            parents = [self.genesis_id or "genesis"]

        # Validate parents exist
        for pid in parents:
            if pid not in self.nodes:
                logger.error(f"Parent {pid} not found")
                return None

        node_id = hashlib.sha256(
            f"{creator}:{datetime.now(timezone.utc).timestamp()}:{len(self.nodes)}".encode()
        ).hexdigest()[:16]

        node = DAGNode(
            node_id=node_id, transactions=transactions,
            parents=parents, creator=creator)
        self.nodes[node_id] = node

        # Update tips
        for pid in parents:
            self.tips.discard(pid)
        self.tips.add(node_id)

        # Index transactions
        for txn in transactions:
            self._txn_index[txn.txn_id] = node_id

        # Update weights and confirmations
        self._update_weights(node_id)

        return node

    def get_transaction(self, txn_id: str) -> Optional[Transaction]:
        node_id = self._txn_index.get(txn_id)
        if not node_id:
            return None
        node = self.nodes.get(node_id)
        if not node:
            return None
        for txn in node.transactions:
            if txn.txn_id == txn_id:
                return txn
        return None

    def is_confirmed(self, txn_id: str) -> bool:
        node_id = self._txn_index.get(txn_id)
        if not node_id:
            return False
        node = self.nodes.get(node_id)
        return node.confirmed if node else False

    def get_balance(self, agent_id: str) -> float:
        balance = 0.0
        for node in self.nodes.values():
            for txn in node.transactions:
                if txn.receiver == agent_id:
                    balance += txn.amount
                if txn.sender == agent_id:
                    balance -= txn.amount
        return balance

    def _update_weights(self, from_node_id: str) -> None:
        """Update cumulative weights up the DAG."""
        visited = set()
        queue = [from_node_id]
        while queue:
            nid = queue.pop(0)
            if nid in visited:
                continue
            visited.add(nid)
            node = self.nodes.get(nid)
            if not node:
                continue
            # Weight = 1 + sum of children referencing this node
            children_weight = sum(
                1 for n in self.nodes.values()
                if nid in n.parents and n.node_id != nid)
            node.weight = 1 + children_weight
            if node.weight >= self.confirmation_threshold:
                node.confirmed = True
            queue.extend(node.parents)

    @property
    def stats(self) -> Dict[str, Any]:
        confirmed = sum(1 for n in self.nodes.values() if n.confirmed)
        return {
            "total_nodes": len(self.nodes),
            "tips": len(self.tips),
            "confirmed_nodes": confirmed,
            "total_transactions": len(self._txn_index),
        }
