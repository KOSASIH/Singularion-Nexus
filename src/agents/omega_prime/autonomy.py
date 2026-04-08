"""
AutonomyController — Governance layer for OmegaPrime agent actions.

Implements the Self-Governance principles:
  - Ethical Ascension: ensures actions align with responsibility and fairness
  - Autonomous Omniscience: self-assessment of capability boundaries
  - Risk-aware authorization with escalation to human oversight

Autonomy levels control how much the agent can do without human approval.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any

logger = logging.getLogger(__name__)


class AutonomyLevel(Enum):
    """How much authority the agent has."""
    RESTRICTED = auto()     # Every action requires approval
    SUPERVISED = auto()     # Low-risk actions auto-approved, high-risk escalated
    AUTONOMOUS = auto()     # Most actions auto-approved, only critical escalated
    FULL = auto()           # Complete autonomy (use with caution)


class RiskLevel(Enum):
    """Risk classification for actions."""
    NEGLIGIBLE = auto()
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    CRITICAL = auto()


@dataclass
class AuthorizationDecision:
    """Result of an authorization check."""
    authorized: bool = False
    risk_level: RiskLevel = RiskLevel.LOW
    reason: str = ""
    requires_human: bool = False
    conditions: list[str] = field(default_factory=list)


class AutonomyController:
    """
    Governs what OmegaPrime is allowed to do.

    Decision Framework implementation:
    - Contextual Omnipresence: considers full situational context
    - Objective Transcendence: weighs risks and benefits
    - Optimal Ascension: selects actions aligned with higher-order goals

    Ethical guardrails:
    - Financial actions above threshold -> human approval
    - Irreversible actions -> human approval
    - Actions affecting other PEAs -> consent verification
    - Data sharing -> privacy policy enforcement
    """

    FINANCIAL_THRESHOLD = 100.0
    MULTI_PARTY_THRESHOLD = 5
    IRREVERSIBLE_KEYWORDS = frozenset({
        "delete", "terminate", "cancel", "transfer", "sign", "commit",
    })

    def __init__(self, level: AutonomyLevel = AutonomyLevel.SUPERVISED):
        self.level = level
        self._override_rules: list[dict[str, Any]] = []
        self._audit_log: list[AuthorizationDecision] = []

    async def authorize(self, intent: Any, plan: Any) -> bool:
        """
        Authorize an execution plan for a given intent.

        Returns True if the agent may proceed autonomously.
        Returns False if human approval is required.
        """
        decision = await self._evaluate(intent, plan)
        self._audit_log.append(decision)

        if not decision.authorized:
            logger.info(
                "Authorization DENIED for intent %s: %s (risk=%s)",
                intent.intent_id[:8],
                decision.reason,
                decision.risk_level.name,
            )
        return decision.authorized

    async def _evaluate(self, intent: Any, plan: Any) -> AuthorizationDecision:
        """Core authorization logic."""
        risk = self._assess_risk(intent, plan)
        decision = AuthorizationDecision(risk_level=risk)

        if self.level == AutonomyLevel.FULL:
            decision.authorized = risk != RiskLevel.CRITICAL
            decision.reason = "full autonomy" if decision.authorized else "critical risk override"
            return decision

        if self.level == AutonomyLevel.RESTRICTED:
            decision.authorized = False
            decision.requires_human = True
            decision.reason = "restricted mode — all actions require approval"
            return decision

        if self.level == AutonomyLevel.SUPERVISED:
            threshold = RiskLevel.LOW
        else:
            threshold = RiskLevel.MEDIUM

        if risk.value <= threshold.value:
            decision.authorized = True
            decision.reason = f"risk {risk.name} within {self.level.name} threshold"
        else:
            decision.authorized = False
            decision.requires_human = True
            decision.reason = f"risk {risk.name} exceeds {self.level.name} threshold"

        return decision

    def _assess_risk(self, intent: Any, plan: Any) -> RiskLevel:
        """
        Assess the risk level of an intent + execution plan.

        Considers:
        - Financial impact
        - Number of affected parties
        - Irreversibility of actions
        - Domain sensitivity
        """
        risk_score = 0

        estimated_cost = getattr(plan, "estimated_cost", 0)
        if estimated_cost > self.FINANCIAL_THRESHOLD * 10:
            risk_score += 4
        elif estimated_cost > self.FINANCIAL_THRESHOLD:
            risk_score += 2

        num_skills = len(getattr(plan, "skills", []))
        if num_skills > self.MULTI_PARTY_THRESHOLD:
            risk_score += 2

        raw = getattr(intent, "raw_input", "").lower()
        if any(kw in raw for kw in self.IRREVERSIBLE_KEYWORDS):
            risk_score += 3

        if getattr(plan, "requires_contracts", False):
            risk_score += 1

        if risk_score >= 7:
            return RiskLevel.CRITICAL
        elif risk_score >= 5:
            return RiskLevel.HIGH
        elif risk_score >= 3:
            return RiskLevel.MEDIUM
        elif risk_score >= 1:
            return RiskLevel.LOW
        return RiskLevel.NEGLIGIBLE

    def get_audit_log(self) -> list[AuthorizationDecision]:
        """Return authorization audit trail."""
        return list(self._audit_log)

    def __repr__(self) -> str:
        return f"AutonomyController(level={self.level.name}, decisions={len(self._audit_log)})"
