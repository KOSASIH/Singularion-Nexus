"""
OmegaPrime Nexus Agent — Core Agent Module

The apex autonomous agent for Singularion Nexus. OmegaPrime transcends single-domain
boundaries by dynamically composing skills, reasoning across heterogeneous data streams,
and self-optimizing its cognitive architecture in real time.

Key capabilities:
  - Cross-domain intent synthesis (travel, energy, housing, finance, health — simultaneously)
  - Recursive self-improvement via meta-learning feedback loops
  - Quantum-accelerated reasoning for combinatorial negotiation spaces
  - ZKP-authenticated delegation chains for trustless multi-agent collaboration
  - Collective intelligence amplification through PEA mesh clustering
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Any, Optional

from .cognition import CognitionEngine, ReasoningMode
from .skill_registry import Skill, SkillRegistry
from .autonomy import AutonomyController, AutonomyLevel

logger = logging.getLogger(__name__)


class AgentState(Enum):
    """Lifecycle states for the OmegaPrime agent."""
    INITIALIZING = auto()
    IDLE = auto()
    REASONING = auto()
    EXECUTING = auto()
    NEGOTIATING = auto()
    EVOLVING = auto()       # Meta-learning / self-optimization phase
    COLLABORATING = auto()  # Multi-agent collective action
    SUSPENDED = auto()
    TERMINATED = auto()


@dataclass
class AgentIdentity:
    """Cryptographic + semantic identity of an OmegaPrime instance."""
    agent_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    mesh_address: str = ""
    public_key: bytes = b""
    reputation_score: float = 1.0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    domains: list[str] = field(default_factory=list)


@dataclass
class IntentRequest:
    """A user or system intent to be fulfilled."""
    intent_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    raw_input: str = ""
    parsed_domains: list[str] = field(default_factory=list)
    constraints: dict[str, Any] = field(default_factory=dict)
    priority: float = 0.5
    deadline: Optional[datetime] = None
    context: dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionResult:
    """Outcome of intent fulfillment."""
    intent_id: str = ""
    success: bool = False
    actions_taken: list[dict[str, Any]] = field(default_factory=list)
    contracts_created: list[str] = field(default_factory=list)
    cost: float = 0.0
    latency_ms: float = 0.0
    reasoning_trace: list[str] = field(default_factory=list)
    meta: dict[str, Any] = field(default_factory=dict)


class OmegaPrimeAgent:
    """
    The OmegaPrime Nexus Agent.

    Serves as the pinnacle autonomous AI within the Singularion Nexus mesh,
    orchestrating cross-domain intent fulfillment with self-evolving cognition.

    Architecture:
        ┌─────────────────────────────────────────┐
        │           OmegaPrime Agent               │
        │  ┌──────────┐  ┌──────────────────────┐ │
        │  │ Cognition │  │   Skill Registry     │ │
        │  │  Engine   │──│  (dynamic loading)   │ │
        │  └──────────┘  └──────────────────────┘ │
        │  ┌──────────┐  ┌──────────────────────┐ │
        │  │ Autonomy  │  │  Mesh Connector      │ │
        │  │ Controller│──│  (PEA collaboration) │ │
        │  └──────────┘  └──────────────────────┘ │
        └─────────────────────────────────────────┘
    """

    def __init__(
        self,
        identity: Optional[AgentIdentity] = None,
        autonomy_level: AutonomyLevel = AutonomyLevel.SUPERVISED,
        reasoning_mode: ReasoningMode = ReasoningMode.HYBRID,
    ):
        self.identity = identity or AgentIdentity()
        self.state = AgentState.INITIALIZING
        self.cognition = CognitionEngine(mode=reasoning_mode)
        self.skills = SkillRegistry()
        self.autonomy = AutonomyController(level=autonomy_level)
        self._intent_queue: asyncio.Queue[IntentRequest] = asyncio.Queue()
        self._execution_history: list[ExecutionResult] = []
        self._evolution_cycle: int = 0

        logger.info(
            "OmegaPrime agent %s initializing | autonomy=%s reasoning=%s",
            self.identity.agent_id[:8],
            autonomy_level.name,
            reasoning_mode.name,
        )

    # ── Lifecycle ──────────────────────────────────────────────────

    async def start(self) -> None:
        """Boot the agent: load skills, connect to mesh, enter main loop."""
        self.state = AgentState.IDLE
        await self.skills.discover_and_load()
        await self.cognition.initialize()
        logger.info("OmegaPrime %s online — %d skills loaded", self.identity.agent_id[:8], len(self.skills))
        await self._main_loop()

    async def shutdown(self) -> None:
        """Graceful shutdown with state persistence."""
        logger.info("OmegaPrime %s shutting down after %d evolution cycles", self.identity.agent_id[:8], self._evolution_cycle)
        self.state = AgentState.TERMINATED
        await self.cognition.persist_state()

    # ── Intent Processing ──────────────────────────────────────────

    async def submit_intent(self, intent: IntentRequest) -> str:
        """Submit an intent for fulfillment. Returns intent_id."""
        await self._intent_queue.put(intent)
        logger.info("Intent %s queued | domains=%s priority=%.2f", intent.intent_id[:8], intent.parsed_domains, intent.priority)
        return intent.intent_id

    async def fulfill_intent(self, intent: IntentRequest) -> ExecutionResult:
        """
        Core fulfillment pipeline:
        1. Decompose intent across domains
        2. Select & compose skills
        3. Reason about optimal strategy (quantum-accelerated if available)
        4. Execute with ZKP-authenticated micro-contracts
        5. Validate outcomes & feed back to meta-learner
        """
        self.state = AgentState.REASONING
        result = ExecutionResult(intent_id=intent.intent_id)

        try:
            # Phase 1: Deep intent understanding
            parsed = await self.cognition.decompose_intent(intent)
            result.reasoning_trace.append(f"decomposed into {len(parsed.sub_intents)} sub-intents")

            # Phase 2: Skill composition
            skill_plan = await self.skills.compose_for_intent(parsed)
            result.reasoning_trace.append(f"composed {len(skill_plan.skills)} skills")

            # Phase 3: Autonomy gate — check if execution is permitted
            if not await self.autonomy.authorize(intent, skill_plan):
                result.reasoning_trace.append("blocked by autonomy controller — escalating to user")
                result.meta["requires_approval"] = True
                return result

            # Phase 4: Execute
            self.state = AgentState.EXECUTING
            for step in skill_plan.execution_steps:
                step_result = await self._execute_step(step, intent.context)
                result.actions_taken.append(step_result)

            # Phase 5: Create micro-contracts via ZKP engine
            if skill_plan.requires_contracts:
                self.state = AgentState.NEGOTIATING
                contracts = await self._negotiate_and_sign(skill_plan, intent)
                result.contracts_created = contracts

            result.success = True

        except Exception as e:
            logger.exception("Intent %s failed: %s", intent.intent_id[:8], e)
            result.meta["error"] = str(e)

        finally:
            self._execution_history.append(result)
            self.state = AgentState.IDLE

        # Meta-learning feedback
        await self._maybe_evolve(result)

        return result

    # ── Self-Evolution ─────────────────────────────────────────────

    async def _maybe_evolve(self, result: ExecutionResult) -> None:
        """
        Trigger meta-learning if performance metrics warrant it.
        OmegaPrime continuously refines its reasoning strategies,
        skill compositions, and negotiation heuristics.
        """
        if self._should_evolve():
            self.state = AgentState.EVOLVING
            self._evolution_cycle += 1
            logger.info("Evolution cycle %d triggered", self._evolution_cycle)
            await self.cognition.meta_learn(self._execution_history[-100:])
            await self.skills.optimize_compositions()
            self.state = AgentState.IDLE

    def _should_evolve(self) -> bool:
        """Heuristic: evolve every 50 intents or on failure streaks."""
        recent = self._execution_history[-10:]
        if len(self._execution_history) % 50 == 0:
            return True
        failure_rate = sum(1 for r in recent if not r.success) / max(len(recent), 1)
        return failure_rate > 0.3

    # ── Collective Intelligence ────────────────────────────────────

    async def form_cluster(self, peer_ids: list[str], objective: str) -> str:
        """
        Form a dynamic PEA cluster for collective bargaining.
        Returns cluster_id for tracking.
        """
        self.state = AgentState.COLLABORATING
        cluster_id = str(uuid.uuid4())
        logger.info(
            "Forming cluster %s with %d peers for: %s",
            cluster_id[:8], len(peer_ids), objective,
        )
        # TODO: Integrate with collective_bargaining module
        # TODO: Shapley value distribution for benefit allocation
        self.state = AgentState.IDLE
        return cluster_id

    # ── Private Helpers ────────────────────────────────────────────

    async def _main_loop(self) -> None:
        """Process intents from the queue."""
        while self.state != AgentState.TERMINATED:
            try:
                intent = await asyncio.wait_for(self._intent_queue.get(), timeout=1.0)
                await self.fulfill_intent(intent)
            except asyncio.TimeoutError:
                continue

    async def _execute_step(self, step: dict, context: dict) -> dict:
        """Execute a single step in the skill plan."""
        # TODO: Implement actual skill execution dispatch
        return {"step": step.get("name", "unknown"), "status": "executed"}

    async def _negotiate_and_sign(self, plan: Any, intent: IntentRequest) -> list[str]:
        """Negotiate and sign ZKP micro-contracts."""
        # TODO: Integrate with zkp_engine for Groth16/PLONK proof generation
        return []

    def __repr__(self) -> str:
        return (
            f"OmegaPrimeAgent(id={self.identity.agent_id[:8]}, "
            f"state={self.state.name}, skills={len(self.skills)}, "
            f"evolutions={self._evolution_cycle})"
        )
