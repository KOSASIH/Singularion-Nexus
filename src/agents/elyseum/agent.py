"""
Elyseum Agent Core - Mastermind of Quantum Innovation

The central orchestrator that unifies quantum cognition, innovation synthesis,
autonomous research, and breakthrough discovery into a single coherent agent.
"""

from __future__ import annotations

import asyncio
import uuid
import time
import logging
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Any, Optional, Callable, Awaitable

logger = logging.getLogger("elyseum.agent")


class AgentState(Enum):
    """Elyseum lifecycle states."""
    DORMANT = auto()
    INITIALIZING = auto()
    CALIBRATING = auto()         # Quantum state calibration
    OBSERVING = auto()           # Passive intelligence gathering
    ANALYZING = auto()           # Deep analysis mode
    INNOVATING = auto()          # Active breakthrough generation
    SYNTHESIZING = auto()        # Cross-domain synthesis
    ORCHESTRATING = auto()       # Multi-agent coordination
    EVOLVING = auto()            # Self-improvement cycle
    TRANSCENDING = auto()        # Paradigm-shift operations
    ERROR_RECOVERY = auto()


class InnovationPriority(Enum):
    """Priority tiers for innovation tasks."""
    CRITICAL_BREAKTHROUGH = 1
    HIGH_IMPACT = 2
    STRATEGIC = 3
    EXPLORATORY = 4
    SPECULATIVE = 5


@dataclass
class InnovationIntent:
    """Represents a quantum innovation intent to be fulfilled."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    domain: str = ""
    objective: str = ""
    priority: InnovationPriority = InnovationPriority.STRATEGIC
    constraints: dict[str, Any] = field(default_factory=dict)
    quantum_parameters: dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)
    status: str = "pending"
    result: Any = None


@dataclass
class BreakthroughResult:
    """Output from a breakthrough synthesis cycle."""
    intent_id: str
    innovation_type: str
    confidence: float
    novelty_score: float
    impact_score: float
    feasibility_score: float
    description: str
    technical_details: dict[str, Any] = field(default_factory=dict)
    research_artifacts: list[dict[str, Any]] = field(default_factory=list)
    cross_domain_links: list[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)

    @property
    def composite_score(self) -> float:
        return (
            self.confidence * 0.2
            + self.novelty_score * 0.3
            + self.impact_score * 0.3
            + self.feasibility_score * 0.2
        )


class ElyseumAgent:
    """
    Elyseum - Mastermind of Quantum Innovation

    Core capabilities:
    1. Quantum Cognition - Superposition-based reasoning across solution spaces
    2. Innovation Synthesis - Cross-domain breakthrough generation
    3. Autonomous Research - Self-directed knowledge acquisition
    4. Paradigm Detection - Identifying and leveraging paradigm shifts
    5. Emergent Tech Discovery - Spotting convergent technology opportunities
    6. Adaptive Strategy - Real-time strategy evolution
    7. Knowledge Fusion - Dynamic multi-domain knowledge integration
    """

    MAX_CONCURRENT_INTENTS = 128
    EVOLUTION_THRESHOLD = 0.85
    QUANTUM_COHERENCE_MIN = 0.7

    def __init__(
        self,
        agent_id: str | None = None,
        config: dict[str, Any] | None = None,
    ):
        self.agent_id = agent_id or f"elyseum-{uuid.uuid4().hex[:12]}"
        self.config = config or {}
        self.state = AgentState.DORMANT
        self._state_history: list[tuple[AgentState, float]] = []

        # Core subsystems (lazy-initialized)
        self._quantum_core: Any = None
        self._innovation_engine: Any = None
        self._breakthrough_synth: Any = None
        self._skill_registry: Any = None
        self._autonomy: Any = None
        self._research_orch: Any = None
        self._knowledge_graph: Any = None

        # Intent processing
        self._intent_queue: asyncio.Queue[InnovationIntent] = asyncio.Queue(
            maxsize=self.MAX_CONCURRENT_INTENTS
        )
        self._active_intents: dict[str, InnovationIntent] = {}
        self._breakthrough_history: list[BreakthroughResult] = []

        # Performance metrics
        self._metrics: dict[str, float] = {
            "intents_processed": 0,
            "breakthroughs_generated": 0,
            "avg_novelty_score": 0.0,
            "avg_impact_score": 0.0,
            "quantum_coherence": 1.0,
            "evolution_cycles": 0,
            "paradigm_shifts_detected": 0,
            "cross_domain_fusions": 0,
        }

        # Lifecycle hooks
        self._on_breakthrough: list[Callable[[BreakthroughResult], Awaitable[None]]] = []
        self._on_state_change: list[Callable[[AgentState, AgentState], Awaitable[None]]] = []
        self._on_evolution: list[Callable[[dict[str, Any]], Awaitable[None]]] = []

        logger.info("Elyseum agent created: %s", self.agent_id)

    # ──────────────────────── Lifecycle ────────────────────────

    async def initialize(self) -> None:
        """Boot all subsystems and enter observation mode."""
        await self._transition(AgentState.INITIALIZING)

        from .quantum_cognition import QuantumCognitionCore
        from .innovation_engine import InnovationEngine
        from .breakthrough_synthesizer import BreakthroughSynthesizer
        from .skill_registry import ElyseumSkillRegistry
        from .autonomy import ElyseumAutonomy
        from .research_orchestrator import ResearchOrchestrator
        from .knowledge_graph import DynamicKnowledgeGraph

        self._quantum_core = QuantumCognitionCore(self.config.get("quantum", {}))
        self._innovation_engine = InnovationEngine(self.config.get("innovation", {}))
        self._breakthrough_synth = BreakthroughSynthesizer(
            quantum_core=self._quantum_core,
            innovation_engine=self._innovation_engine,
        )
        self._skill_registry = ElyseumSkillRegistry()
        self._autonomy = ElyseumAutonomy(self.config.get("autonomy", {}))
        self._research_orch = ResearchOrchestrator(
            knowledge_graph=None  # set after graph init
        )
        self._knowledge_graph = DynamicKnowledgeGraph(
            self.config.get("knowledge_graph", {})
        )
        self._research_orch._knowledge_graph = self._knowledge_graph

        await self._quantum_core.initialize()
        await self._innovation_engine.initialize()
        await self._knowledge_graph.initialize()
        await self._skill_registry.discover_skills()

        await self._transition(AgentState.CALIBRATING)
        await self._calibrate_quantum_state()
        await self._transition(AgentState.OBSERVING)

        logger.info("Elyseum agent initialized and observing.")

    async def shutdown(self) -> None:
        """Gracefully shut down all subsystems."""
        logger.info("Elyseum shutting down...")
        for intent in list(self._active_intents.values()):
            intent.status = "cancelled"
        self._active_intents.clear()

        if self._knowledge_graph:
            await self._knowledge_graph.persist()
        if self._quantum_core:
            await self._quantum_core.decohere()

        await self._transition(AgentState.DORMANT)

    # ──────────────────────── Intent Pipeline ────────────────────────

    async def submit_intent(self, intent: InnovationIntent) -> str:
        """Submit an innovation intent for processing."""
        await self._intent_queue.put(intent)
        logger.info("Intent submitted: %s [%s]", intent.id, intent.domain)
        return intent.id

    async def process_intents(self) -> list[BreakthroughResult]:
        """Process all queued intents through the innovation pipeline."""
        await self._transition(AgentState.ANALYZING)
        results: list[BreakthroughResult] = []

        while not self._intent_queue.empty():
            intent = await self._intent_queue.get()
            intent.status = "processing"
            self._active_intents[intent.id] = intent

            try:
                result = await self._process_single_intent(intent)
                results.append(result)
                intent.status = "completed"
                intent.result = result
                self._breakthrough_history.append(result)
                self._metrics["intents_processed"] += 1
                self._metrics["breakthroughs_generated"] += 1

                for callback in self._on_breakthrough:
                    await callback(result)

            except Exception as e:
                logger.error("Intent %s failed: %s", intent.id, e)
                intent.status = "failed"

            finally:
                self._active_intents.pop(intent.id, None)

        await self._update_aggregate_metrics()
        await self._check_evolution_trigger()
        return results

    async def _process_single_intent(
        self, intent: InnovationIntent
    ) -> BreakthroughResult:
        """Full pipeline for a single innovation intent."""
        # 1. Quantum analysis - explore solution superposition
        await self._transition(AgentState.ANALYZING)
        quantum_state = await self._quantum_core.analyze(
            domain=intent.domain,
            objective=intent.objective,
            parameters=intent.quantum_parameters,
        )

        # 2. Knowledge graph enrichment
        context = await self._knowledge_graph.query_context(
            domain=intent.domain,
            objective=intent.objective,
        )

        # 3. Research orchestration
        research = await self._research_orch.research(
            intent=intent,
            quantum_state=quantum_state,
            existing_context=context,
        )

        # 4. Innovation synthesis
        await self._transition(AgentState.INNOVATING)
        innovation = await self._innovation_engine.generate(
            intent=intent,
            quantum_state=quantum_state,
            research=research,
            context=context,
        )

        # 5. Breakthrough synthesis - cross-domain fusion
        await self._transition(AgentState.SYNTHESIZING)
        breakthrough = await self._breakthrough_synth.synthesize(
            intent=intent,
            innovation=innovation,
            quantum_state=quantum_state,
        )

        # 6. Update knowledge graph
        await self._knowledge_graph.integrate_breakthrough(breakthrough)

        return breakthrough

    # ──────────────────────── Quantum Calibration ────────────────────────

    async def _calibrate_quantum_state(self) -> None:
        """Calibrate quantum coherence for optimal reasoning."""
        if self._quantum_core:
            coherence = await self._quantum_core.calibrate()
            self._metrics["quantum_coherence"] = coherence
            if coherence < self.QUANTUM_COHERENCE_MIN:
                logger.warning(
                    "Quantum coherence below threshold: %.3f < %.3f",
                    coherence,
                    self.QUANTUM_COHERENCE_MIN,
                )
                await self._quantum_core.recalibrate()

    # ──────────────────────── Evolution ────────────────────────

    async def _check_evolution_trigger(self) -> None:
        """Check if performance warrants an evolution cycle."""
        if not self._breakthrough_history:
            return

        recent = self._breakthrough_history[-20:]
        avg_composite = sum(b.composite_score for b in recent) / len(recent)

        if avg_composite >= self.EVOLUTION_THRESHOLD:
            await self._evolve()

    async def _evolve(self) -> None:
        """Execute a self-evolution cycle."""
        await self._transition(AgentState.EVOLVING)
        self._metrics["evolution_cycles"] += 1

        evolution_report: dict[str, Any] = {
            "cycle": self._metrics["evolution_cycles"],
            "timestamp": time.time(),
            "improvements": [],
        }

        # Optimize quantum parameters
        if self._quantum_core:
            q_improvement = await self._quantum_core.optimize()
            evolution_report["improvements"].append(
                {"subsystem": "quantum_cognition", "detail": q_improvement}
            )

        # Optimize innovation engine
        if self._innovation_engine:
            i_improvement = await self._innovation_engine.optimize(
                history=self._breakthrough_history[-50:]
            )
            evolution_report["improvements"].append(
                {"subsystem": "innovation_engine", "detail": i_improvement}
            )

        # Re-rank skills
        if self._skill_registry:
            await self._skill_registry.rerank_skills(self._metrics)

        for callback in self._on_evolution:
            await callback(evolution_report)

        await self._transition(AgentState.OBSERVING)
        logger.info("Evolution cycle %d complete.", self._metrics["evolution_cycles"])

    # ──────────────────────── Multi-Agent Coordination ────────────────────────

    async def coordinate(
        self,
        agents: list[Any],
        objective: str,
        strategy: str = "consensus",
    ) -> dict[str, Any]:
        """Orchestrate multi-agent collaboration for complex innovation."""
        await self._transition(AgentState.ORCHESTRATING)

        coordination_plan = await self._innovation_engine.plan_coordination(
            agents=agents,
            objective=objective,
            strategy=strategy,
        )

        results: dict[str, Any] = {"plan": coordination_plan, "agent_outputs": {}}
        tasks = []
        for agent_assignment in coordination_plan.get("assignments", []):
            agent = agent_assignment["agent"]
            task_desc = agent_assignment["task"]
            tasks.append(self._delegate_to_agent(agent, task_desc))

        outputs = await asyncio.gather(*tasks, return_exceptions=True)
        for assignment, output in zip(
            coordination_plan.get("assignments", []), outputs
        ):
            agent_id = assignment.get("agent_id", "unknown")
            if isinstance(output, Exception):
                results["agent_outputs"][agent_id] = {"error": str(output)}
            else:
                results["agent_outputs"][agent_id] = output

        # Fuse results
        fused = await self._breakthrough_synth.fuse_multi_agent(
            results["agent_outputs"]
        )
        results["fused_output"] = fused
        self._metrics["cross_domain_fusions"] += 1

        await self._transition(AgentState.OBSERVING)
        return results

    async def _delegate_to_agent(
        self, agent: Any, task: str
    ) -> dict[str, Any]:
        """Delegate a subtask to another agent."""
        if hasattr(agent, "execute"):
            return await agent.execute(task)
        return {"status": "unsupported", "task": task}

    # ──────────────────────── Paradigm Shift Detection ────────────────────────

    async def detect_paradigm_shifts(self) -> list[dict[str, Any]]:
        """Analyze breakthrough history for paradigm-level shifts."""
        await self._transition(AgentState.TRANSCENDING)

        shifts = await self._innovation_engine.detect_paradigm_shifts(
            breakthroughs=self._breakthrough_history,
            knowledge_graph=self._knowledge_graph,
        )

        self._metrics["paradigm_shifts_detected"] += len(shifts)
        await self._transition(AgentState.OBSERVING)
        return shifts

    # ──────────────────────── State Management ────────────────────────

    async def _transition(self, new_state: AgentState) -> None:
        old_state = self.state
        if old_state == new_state:
            return
        self.state = new_state
        self._state_history.append((new_state, time.time()))
        for callback in self._on_state_change:
            await callback(old_state, new_state)

    # ──────────────────────── Metrics ────────────────────────

    async def _update_aggregate_metrics(self) -> None:
        if self._breakthrough_history:
            recent = self._breakthrough_history[-100:]
            self._metrics["avg_novelty_score"] = (
                sum(b.novelty_score for b in recent) / len(recent)
            )
            self._metrics["avg_impact_score"] = (
                sum(b.impact_score for b in recent) / len(recent)
            )

    def get_metrics(self) -> dict[str, Any]:
        return {**self._metrics, "state": self.state.name}

    # ──────────────────────── Hooks ────────────────────────

    def on_breakthrough(
        self, callback: Callable[[BreakthroughResult], Awaitable[None]]
    ) -> None:
        self._on_breakthrough.append(callback)

    def on_state_change(
        self, callback: Callable[[AgentState, AgentState], Awaitable[None]]
    ) -> None:
        self._on_state_change.append(callback)

    def on_evolution(
        self, callback: Callable[[dict[str, Any]], Awaitable[None]]
    ) -> None:
        self._on_evolution.append(callback)

    def __repr__(self) -> str:
        return (
            f"ElyseumAgent(id={self.agent_id!r}, state={self.state.name}, "
            f"breakthroughs={len(self._breakthrough_history)})"
        )
