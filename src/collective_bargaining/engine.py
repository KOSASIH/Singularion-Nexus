"""Collective Bargaining Engine.

Enables PEAs to form dynamic clusters for group negotiations,
such as neighborhoods negotiating bulk utility rates.
"""

import hashlib
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


@dataclass
class BargainingCluster:
    cluster_id: str
    domain: str
    members: Set[str] = field(default_factory=set)
    target_entity: str = ""
    aggregated_demand: Dict[str, Any] = field(default_factory=dict)
    status: str = "forming"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    min_members: int = 10
    max_members: int = 10000

    @property
    def size(self) -> int:
        return len(self.members)

    @property
    def is_viable(self) -> bool:
        return self.size >= self.min_members


class CollectiveBargainingEngine:
    def __init__(self):
        self.clusters: Dict[str, BargainingCluster] = {}
        self.active_negotiations: Dict[str, List] = {}

    async def create_cluster(self, domain: str, initial_members: Set[str], target_entity: str, min_members: int = 10) -> BargainingCluster:
        cid = hashlib.sha256(f"{domain}:{target_entity}:{datetime.now(timezone.utc).timestamp()}".encode()).hexdigest()[:12]
        cluster = BargainingCluster(cluster_id=cid, domain=domain, members=initial_members, target_entity=target_entity, min_members=min_members)
        self.clusters[cid] = cluster
        logger.info(f"Cluster created: {cid} - domain={domain}, members={cluster.size}")
        return cluster

    async def join_cluster(self, cluster_id: str, pea_id: str) -> bool:
        cluster = self.clusters.get(cluster_id)
        if not cluster or cluster.size >= cluster.max_members:
            return False
        cluster.members.add(pea_id)
        return True

    async def start_negotiation(self, cluster_id: str) -> bool:
        cluster = self.clusters.get(cluster_id)
        if not cluster or not cluster.is_viable:
            return False
        cluster.status = "negotiating"
        self.active_negotiations[cluster_id] = []
        return True

    async def calculate_benefit_distribution(self, cluster_id: str, total_savings: float) -> Dict[str, float]:
        cluster = self.clusters.get(cluster_id)
        if not cluster:
            return {}
        equal_share = total_savings / cluster.size
        return {m: equal_share for m in cluster.members}
