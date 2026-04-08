"""Intent Fulfillment Router — Multi-criteria path selection."""

import hashlib
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


@dataclass
class FulfillmentPath:
    path_id: str
    provider_pea_id: str
    domain: str
    estimated_cost: float
    estimated_time_seconds: float
    quality_score: float
    hops: int
    requires_zkp: bool = True
    reputation: float = 0.5


@dataclass
class RoutingDecision:
    intent_id: str
    selected_path: FulfillmentPath
    alternatives: List[FulfillmentPath] = field(default_factory=list)
    reasoning: str = ""
    confidence: float = 0.0
    decided_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ServiceRegistration:
    provider_id: str
    domain: str
    capabilities: List[str]
    pricing: Dict[str, float]
    quality_score: float = 0.5
    availability: float = 1.0
    registered_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class IntentRouter:
    def __init__(self):
        self.services: Dict[str, List[ServiceRegistration]] = {}
        self.routing_history: List[RoutingDecision] = []
        for d in ["travel", "housing", "energy", "telecom", "finance", "healthcare"]:
            self.services[d] = []

    def register_service(self, registration: ServiceRegistration) -> bool:
        self.services.setdefault(registration.domain, []).append(registration)
        return True

    async def find_paths(self, intent_id: str, domain: str,
                        requirements: Dict[str, Any], max_paths: int = 5) -> List[FulfillmentPath]:
        registered = self.services.get(domain, [])
        paths = []
        for svc in registered[:max_paths]:
            pid = hashlib.sha256(f"{intent_id}:{svc.provider_id}".encode()).hexdigest()[:12]
            paths.append(FulfillmentPath(
                path_id=pid, provider_pea_id=svc.provider_id,
                domain=domain, estimated_cost=svc.pricing.get("base", 100.0),
                estimated_time_seconds=5.0, quality_score=svc.quality_score,
                hops=1, reputation=svc.availability))
        return paths

    async def select_optimal_path(
        self, intent_id: str, paths: List[FulfillmentPath],
        preferences: Optional[Dict[str, float]] = None,
    ) -> RoutingDecision:
        if not paths:
            raise ValueError(f"No paths for intent {intent_id}")
        prefs = preferences or {"cost": 0.3, "quality": 0.4, "time": 0.2, "reputation": 0.1}

        def score(p: FulfillmentPath) -> float:
            cost_score = 1.0 / (1.0 + p.estimated_cost * 0.01)
            time_score = 1.0 / (1.0 + p.estimated_time_seconds * 0.01)
            return (prefs.get("cost", 0.3) * cost_score +
                    prefs.get("quality", 0.4) * p.quality_score +
                    prefs.get("time", 0.2) * time_score +
                    prefs.get("reputation", 0.1) * p.reputation)

        ranked = sorted(paths, key=score, reverse=True)
        decision = RoutingDecision(
            intent_id=intent_id, selected_path=ranked[0],
            alternatives=ranked[1:], confidence=score(ranked[0]),
            reasoning=f"Selected based on weighted criteria: {prefs}")
        self.routing_history.append(decision)
        return decision

    async def execute_fulfillment(self, decision: RoutingDecision) -> Dict[str, Any]:
        return {
            "status": "executing", "path_id": decision.selected_path.path_id,
            "intent_id": decision.intent_id,
            "provider": decision.selected_path.provider_pea_id}
