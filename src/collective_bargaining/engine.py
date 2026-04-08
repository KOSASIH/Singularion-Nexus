"""Collective Bargaining Engine — Cluster formation, negotiation, Shapley distribution."""

import hashlib
import logging
import math
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

    @property
    def bargaining_power(self) -> float:
        """Logarithmic bargaining power based on cluster size."""
        if self.size <= 1:
            return 0.0
        return min(1.0, math.log2(self.size) / 15.0)


@dataclass
class NegotiationRound:
    round_number: int
    proposal: Dict[str, Any]
    counterproposal: Optional[Dict[str, Any]] = None
    cluster_vote: Optional[float] = None
    accepted: bool = False
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class CollectiveBargainingEngine:
    def __init__(self):
        self.clusters: Dict[str, BargainingCluster] = {}
        self.negotiations: Dict[str, List[NegotiationRound]] = {}
        self._completed_negotiations = 0

    async def create_cluster(self, domain: str, initial_members: Set[str],
                            target_entity: str, min_members: int = 10) -> BargainingCluster:
        cid = hashlib.sha256(
            f"{domain}:{target_entity}:{datetime.now(timezone.utc).timestamp()}".encode()
        ).hexdigest()[:12]
        cluster = BargainingCluster(
            cluster_id=cid, domain=domain, members=initial_members,
            target_entity=target_entity, min_members=min_members)
        self.clusters[cid] = cluster
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
        cluster.aggregated_demand = await self._aggregate_preferences(cluster)
        self.negotiations[cluster_id] = []
        return True

    async def submit_round(self, cluster_id: str, proposal: Dict[str, Any],
                          counterproposal: Optional[Dict[str, Any]] = None,
                          approval_rate: float = 0.0) -> Optional[NegotiationRound]:
        if cluster_id not in self.negotiations:
            return None
        rounds = self.negotiations[cluster_id]
        rnd = NegotiationRound(
            round_number=len(rounds) + 1, proposal=proposal,
            counterproposal=counterproposal, cluster_vote=approval_rate,
            accepted=approval_rate >= 0.67)
        rounds.append(rnd)
        if rnd.accepted:
            cluster = self.clusters[cluster_id]
            cluster.status = "settled"
            self._completed_negotiations += 1
        return rnd

    async def calculate_benefit_distribution(
        self, cluster_id: str, total_savings: float
    ) -> Dict[str, float]:
        """Shapley-inspired fair distribution."""
        cluster = self.clusters.get(cluster_id)
        if not cluster or cluster.size == 0:
            return {}
        base_share = total_savings / cluster.size
        # Early joiners get slight bonus (incentive to form clusters)
        members = sorted(cluster.members)
        distribution = {}
        for i, m in enumerate(members):
            position_bonus = 1.0 + 0.1 * max(0, (cluster.size - i) / cluster.size - 0.5)
            distribution[m] = base_share * position_bonus
        # Normalize to exact total
        total_distributed = sum(distribution.values())
        if total_distributed > 0:
            factor = total_savings / total_distributed
            distribution = {m: v * factor for m, v in distribution.items()}
        return distribution

    async def _aggregate_preferences(self, cluster: BargainingCluster) -> Dict[str, Any]:
        return {
            "member_count": cluster.size,
            "bargaining_power": cluster.bargaining_power,
            "domain": cluster.domain,
            "target": cluster.target_entity,
        }
