"""
Elyseum Autonomy Controller - Governance, risk assessment, and authorization.

Manages the agent's autonomy level and ensures innovations stay within
ethical and strategic boundaries.
"""

from __future__ import annotations

import time
import logging
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger("elyseum.autonomy")


class GovernanceLevel(Enum):
    RESTRICTED = 1     # All actions require approval
    GUIDED = 2         # Low-risk actions auto-approved
    AUTONOMOUS = 3     # Most actions auto-approved
    SOVEREIGN = 4      # Full autonomy with audit trail


@dataclass
class AuthorizationRequest:
    """Request for action authorization."""
    action: str
    risk_level: float       # 0.0 (safe) to 1.0 (critical)
    domain: str
    description: str
    requested_at: float = field(default_factory=time.time)


@dataclass
class AuditEntry:
    """Immutable audit trail entry."""
    action: str
    authorized: bool
    governance_level: GovernanceLevel
    risk_level: float
    reason: str
    timestamp: float = field(default_factory=time.time)


class ElyseumAutonomy:
    """
    Governs the agent's autonomy level and authorization policies.

    Features:
    - 4-tier governance (Restricted → Sovereign)
    - Risk-based auto-authorization
    - Full audit trail
    - Dynamic governance escalation/de-escalation
    - Ethical boundary enforcement
    """

    RISK_THRESHOLDS: dict[GovernanceLevel, float] = {
        GovernanceLevel.RESTRICTED: 0.0,
        GovernanceLevel.GUIDED: 0.3,
        GovernanceLevel.AUTONOMOUS: 0.7,
        GovernanceLevel.SOVEREIGN: 0.95,
    }

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self._level = GovernanceLevel(
            self.config.get("governance_level", GovernanceLevel.GUIDED.value)
        )
        self._audit_trail: list[AuditEntry] = []
        self._ethical_boundaries: list[str] = [
            "No actions that harm individuals or groups",
            "No deception or manipulation",
            "Respect privacy and data sovereignty",
            "Ensure transparency in decision-making",
            "Maintain fairness and non-discrimination",
        ]

    @property
    def governance_level(self) -> GovernanceLevel:
        return self._level

    def authorize(self, request: AuthorizationRequest) -> bool:
        """Evaluate an authorization request against current governance level."""
        threshold = self.RISK_THRESHOLDS[self._level]
        authorized = request.risk_level <= threshold

        entry = AuditEntry(
            action=request.action,
            authorized=authorized,
            governance_level=self._level,
            risk_level=request.risk_level,
            reason=(
                f"Risk {request.risk_level:.2f} <= threshold {threshold:.2f}"
                if authorized
                else f"Risk {request.risk_level:.2f} > threshold {threshold:.2f}"
            ),
        )
        self._audit_trail.append(entry)

        logger.info(
            "Authorization [%s]: action=%s, risk=%.2f, level=%s",
            "GRANTED" if authorized else "DENIED",
            request.action,
            request.risk_level,
            self._level.name,
        )
        return authorized

    def escalate(self) -> GovernanceLevel:
        """Escalate governance level."""
        levels = list(GovernanceLevel)
        idx = levels.index(self._level)
        if idx < len(levels) - 1:
            self._level = levels[idx + 1]
            logger.info("Governance escalated to %s", self._level.name)
        return self._level

    def de_escalate(self) -> GovernanceLevel:
        """De-escalate governance level."""
        levels = list(GovernanceLevel)
        idx = levels.index(self._level)
        if idx > 0:
            self._level = levels[idx - 1]
            logger.info("Governance de-escalated to %s", self._level.name)
        return self._level

    def get_audit_trail(self, last_n: int = 50) -> list[AuditEntry]:
        return self._audit_trail[-last_n:]

    def check_ethical_boundary(self, action_description: str) -> bool:
        """Check if an action violates ethical boundaries."""
        # Simplified check - in production this would use NLP
        violation_keywords = ["harm", "deceive", "spy", "steal", "manipulate"]
        lower = action_description.lower()
        for keyword in violation_keywords:
            if keyword in lower:
                logger.warning("Ethical boundary violation detected: %s", keyword)
                return False
        return True
