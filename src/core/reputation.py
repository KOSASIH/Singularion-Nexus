"""Reputation System — Bayesian trust scoring for PEA agents."""

import math
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Tuple
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


@dataclass
class ReputationEvent:
    event_id: str
    subject_id: str
    reporter_id: str
    event_type: str
    score_delta: float
    weight: float = 1.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ReputationProfile:
    agent_id: str
    trust_score: float = 0.5
    transaction_count: int = 0
    successful_transactions: int = 0
    dispute_count: int = 0
    cooperation_score: float = 0.5
    history: List[ReputationEvent] = field(default_factory=list)
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def success_rate(self) -> float:
        if self.transaction_count == 0:
            return 0.5
        return self.successful_transactions / self.transaction_count

    @property
    def reliability_score(self) -> float:
        alpha = self.successful_transactions + 2
        beta = (self.transaction_count - self.successful_transactions) + 2
        bayesian = alpha / (alpha + beta)
        dispute_penalty = max(0, 1.0 - (self.dispute_count * 0.05))
        return bayesian * dispute_penalty


class ReputationEngine:
    def __init__(self, decay_days: float = 90.0):
        self.profiles: Dict[str, ReputationProfile] = {}
        self.decay_days = decay_days

    def get_or_create_profile(self, agent_id: str) -> ReputationProfile:
        if agent_id not in self.profiles:
            self.profiles[agent_id] = ReputationProfile(agent_id=agent_id)
        return self.profiles[agent_id]

    def record_event(self, event: ReputationEvent) -> float:
        profile = self.get_or_create_profile(event.subject_id)
        profile.history.append(event)
        if "success" in event.event_type:
            profile.transaction_count += 1
            profile.successful_transactions += 1
        elif "fail" in event.event_type:
            profile.transaction_count += 1
        elif "dispute" in event.event_type:
            profile.dispute_count += 1
        elif "cooperation" in event.event_type:
            profile.cooperation_score = min(1.0, profile.cooperation_score + 0.02)
        profile.trust_score = self._compute_trust(profile)
        profile.last_updated = datetime.now(timezone.utc)
        return profile.trust_score

    def _compute_trust(self, profile: ReputationProfile) -> float:
        if not profile.history:
            return 0.5
        now = datetime.now(timezone.utc)
        ws, wt = 0.0, 0.0
        for ev in profile.history:
            age = (now - ev.timestamp).total_seconds() / 86400
            decay = math.exp(-age / self.decay_days)
            w = ev.weight * decay
            ws += ev.score_delta * w
            wt += w
        if wt == 0:
            return 0.5
        raw = ws / wt
        normalized = 1.0 / (1.0 + math.exp(-4 * (raw - 0.5)))
        blended = 0.6 * normalized + 0.4 * profile.reliability_score
        return max(0.0, min(1.0, blended))

    def get_trust_score(self, agent_id: str) -> float:
        p = self.profiles.get(agent_id)
        return p.trust_score if p else 0.5

    def is_trusted(self, agent_id: str, threshold: float = 0.4) -> bool:
        return self.get_trust_score(agent_id) >= threshold

    def get_top_agents(self, n: int = 10) -> List[Tuple[str, float]]:
        scored = [(a, p.trust_score) for a, p in self.profiles.items()]
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:n]
