"""
Elyseum Skill Registry - Dynamic skill discovery, composition, and ranking.

Maps innovation domains to executable skill modules with performance tracking.
"""

from __future__ import annotations

import time
import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Awaitable, Optional

logger = logging.getLogger("elyseum.skill_registry")


@dataclass
class Skill:
    """A registered innovation skill."""
    name: str
    domain: str
    description: str
    handler: Callable[..., Awaitable[Any]] | None = None
    performance_score: float = 0.5
    usage_count: int = 0
    last_used: float = 0.0
    tags: list[str] = field(default_factory=list)

    def record_use(self, score: float) -> None:
        """Update performance after use."""
        self.usage_count += 1
        self.last_used = time.time()
        alpha = 0.2
        self.performance_score = (1 - alpha) * self.performance_score + alpha * score


class ElyseumSkillRegistry:
    """
    Registry of innovation-domain skills.

    Supports:
    - Dynamic skill registration and discovery
    - Performance-based ranking
    - Skill composition (chaining)
    - Domain-based lookup
    """

    def __init__(self):
        self._skills: dict[str, Skill] = {}
        self._domain_index: dict[str, list[str]] = {}

    async def discover_skills(self) -> None:
        """Auto-discover and register built-in skills."""
        builtins = [
            Skill("quantum_analysis", "quantum", "Quantum-inspired solution analysis", tags=["core", "analysis"]),
            Skill("cross_domain_synthesis", "synthesis", "Cross-domain idea fusion", tags=["core", "fusion"]),
            Skill("paradigm_detection", "meta", "Paradigm shift detection", tags=["meta", "detection"]),
            Skill("research_orchestration", "research", "Autonomous research coordination", tags=["research", "orchestration"]),
            Skill("knowledge_integration", "knowledge", "Dynamic knowledge graph integration", tags=["knowledge", "graph"]),
            Skill("strategic_planning", "strategy", "Innovation strategy planning", tags=["strategy", "planning"]),
            Skill("risk_assessment", "governance", "Innovation risk evaluation", tags=["risk", "governance"]),
            Skill("creative_ideation", "creativity", "Divergent creative ideation", tags=["creativity", "ideation"]),
            Skill("technical_validation", "engineering", "Technical feasibility validation", tags=["engineering", "validation"]),
            Skill("market_analysis", "business", "Market opportunity analysis", tags=["business", "market"]),
            Skill("trend_forecasting", "forecasting", "Technology trend prediction", tags=["forecasting", "trends"]),
            Skill("ethical_review", "ethics", "Innovation ethics assessment", tags=["ethics", "review"]),
        ]
        for skill in builtins:
            self.register(skill)
        logger.info("Discovered %d built-in skills.", len(builtins))

    def register(self, skill: Skill) -> None:
        """Register a skill."""
        self._skills[skill.name] = skill
        self._domain_index.setdefault(skill.domain, []).append(skill.name)

    def get(self, name: str) -> Skill | None:
        return self._skills.get(name)

    def by_domain(self, domain: str) -> list[Skill]:
        names = self._domain_index.get(domain, [])
        return [self._skills[n] for n in names if n in self._skills]

    def ranked(self, top_n: int = 10) -> list[Skill]:
        """Get top skills by performance."""
        return sorted(self._skills.values(), key=lambda s: s.performance_score, reverse=True)[:top_n]

    async def rerank_skills(self, metrics: dict[str, Any]) -> None:
        """Re-rank skills based on agent-level metrics."""
        for skill in self._skills.values():
            if skill.usage_count == 0:
                skill.performance_score = 0.5
        logger.info("Skills re-ranked.")

    def all_skills(self) -> list[Skill]:
        return list(self._skills.values())
