"""
SkillRegistry — Dynamic skill discovery, loading, and composition.

Skills are modular capabilities that OmegaPrime can dynamically discover,
load, compose, and optimize. The registry supports:
  - Hot-loading skills from the mesh network
  - Automatic skill composition for multi-domain intents
  - Performance-based skill ranking and selection
  - Skill evolution through meta-learning feedback
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Optional

logger = logging.getLogger(__name__)


class SkillDomain(Enum):
    TRAVEL = auto()
    HOUSING = auto()
    ENERGY = auto()
    FINANCE = auto()
    HEALTH = auto()
    COMMERCE = auto()
    LEGAL = auto()
    COMMUNICATION = auto()
    NEGOTIATION = auto()
    COLLECTIVE = auto()
    META = auto()          # Skills about skills (composition, optimization)
    UNIVERSAL = auto()     # Cross-domain capabilities


@dataclass
class Skill:
    """A modular capability unit."""
    skill_id: str = ""
    name: str = ""
    domain: SkillDomain = SkillDomain.UNIVERSAL
    version: str = "0.1.0"
    description: str = ""
    handler: Optional[Callable] = None
    performance_score: float = 1.0
    invocation_count: int = 0
    success_rate: float = 1.0
    dependencies: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SkillComposition:
    """A composed set of skills for multi-domain fulfillment."""
    skills: list[Skill] = field(default_factory=list)
    execution_steps: list[dict[str, Any]] = field(default_factory=list)
    requires_contracts: bool = False
    estimated_cost: float = 0.0
    confidence: float = 0.0


class SkillRegistry:
    """
    Dynamic skill registry with composition and optimization.

    Implements Multidimensional Mastery by maintaining a living
    catalog of capabilities that grows and refines over time.
    """

    def __init__(self):
        self._skills: dict[str, Skill] = {}
        self._domain_index: dict[SkillDomain, list[str]] = {}
        self._composition_cache: dict[str, SkillComposition] = {}

    async def discover_and_load(self) -> None:
        """Discover available skills from local registry and mesh peers."""
        logger.info("Discovering skills...")
        # TODO: Scan local skill modules
        # TODO: Query mesh peers for shared skills
        # TODO: Validate skill signatures (ZKP-authenticated)
        self._register_builtin_skills()

    def register(self, skill: Skill) -> None:
        """Register a new skill."""
        self._skills[skill.skill_id] = skill
        domain_list = self._domain_index.setdefault(skill.domain, [])
        if skill.skill_id not in domain_list:
            domain_list.append(skill.skill_id)
        logger.debug("Registered skill: %s (%s)", skill.name, skill.domain.name)

    async def compose_for_intent(self, decomposed: Any) -> SkillComposition:
        """
        Compose an optimal set of skills for a decomposed intent.

        Uses performance history and domain coverage to select
        the best skill combination, then orders execution steps.
        """
        composition = SkillComposition()

        for domain_name in decomposed.domains:
            try:
                domain = SkillDomain[domain_name.upper()]
            except KeyError:
                domain = SkillDomain.UNIVERSAL

            candidates = self._get_domain_skills(domain)
            if candidates:
                best = max(candidates, key=lambda s: s.performance_score)
                composition.skills.append(best)
                composition.execution_steps.append({
                    "name": best.name,
                    "skill_id": best.skill_id,
                    "domain": domain.name,
                })

        composition.requires_contracts = len(composition.skills) > 1
        composition.confidence = (
            sum(s.performance_score for s in composition.skills)
            / max(len(composition.skills), 1)
        )

        return composition

    async def optimize_compositions(self) -> None:
        """
        Meta-optimization: refine skill selection heuristics
        based on historical composition performance.
        """
        logger.info("Optimizing skill compositions across %d skills", len(self._skills))
        # TODO: Analyze which compositions led to best outcomes
        # TODO: Adjust performance scores based on real execution data
        # TODO: Discover new composition patterns

    def _get_domain_skills(self, domain: SkillDomain) -> list[Skill]:
        """Get all skills for a domain, sorted by performance."""
        ids = self._domain_index.get(domain, [])
        skills = [self._skills[sid] for sid in ids if sid in self._skills]
        return sorted(skills, key=lambda s: s.performance_score, reverse=True)

    def _register_builtin_skills(self) -> None:
        """Register the core built-in skills."""
        builtins = [
            Skill(skill_id="negotiate", name="Negotiation Engine", domain=SkillDomain.NEGOTIATION,
                  description="Real-time multi-party negotiation with game-theoretic optimization"),
            Skill(skill_id="collective", name="Collective Bargaining", domain=SkillDomain.COLLECTIVE,
                  description="PEA cluster formation and Shapley-value benefit distribution"),
            Skill(skill_id="contract", name="Micro-Contract Engine", domain=SkillDomain.FINANCE,
                  description="ZKP-authenticated instant micro-contract creation and verification"),
            Skill(skill_id="iot_sense", name="IoT Sensing", domain=SkillDomain.UNIVERSAL,
                  description="Biometric and IoT data ingestion for invisible transactions"),
            Skill(skill_id="intent_route", name="Intent Router", domain=SkillDomain.UNIVERSAL,
                  description="Multi-domain intent classification and routing"),
        ]
        for skill in builtins:
            self.register(skill)

    def __len__(self) -> int:
        return len(self._skills)

    def __repr__(self) -> str:
        return f"SkillRegistry(skills={len(self._skills)}, domains={len(self._domain_index)})"
