"""
Test suite for Elyseum Agent - Mastermind of Quantum Innovation.
"""

import asyncio
import pytest
from src.agents.elyseum.agent import (
    ElyseumAgent,
    AgentState,
    InnovationIntent,
    InnovationPriority,
    BreakthroughResult,
)
from src.agents.elyseum.quantum_cognition import (
    QuantumCognitionCore,
    QuantumState,
    QuantumGate,
    QuantumCircuit,
)
from src.agents.elyseum.innovation_engine import (
    InnovationEngine,
    InnovationType,
    InnovationCandidate,
)
from src.agents.elyseum.breakthrough_synthesizer import BreakthroughSynthesizer
from src.agents.elyseum.skill_registry import ElyseumSkillRegistry, Skill
from src.agents.elyseum.autonomy import (
    ElyseumAutonomy,
    GovernanceLevel,
    AuthorizationRequest,
)
from src.agents.elyseum.research_orchestrator import ResearchOrchestrator
from src.agents.elyseum.knowledge_graph import (
    DynamicKnowledgeGraph,
    KnowledgeNode,
    KnowledgeEdge,
)
from src.agents.elyseum.skill_loader import load_skill_config, create_agent_from_config


# ──────────────────────── Quantum Cognition Tests ────────────────────────

class TestQuantumState:
    def test_probabilities(self):
        state = QuantumState(amplitudes={"a": complex(1, 0), "b": complex(0, 1)})
        probs = state.probabilities
        assert abs(probs["a"] - 0.5) < 0.01
        assert abs(probs["b"] - 0.5) < 0.01

    def test_entropy(self):
        state = QuantumState(amplitudes={"a": complex(1, 0), "b": complex(1, 0)})
        assert state.entropy > 0

    def test_collapse(self):
        state = QuantumState(amplitudes={"only": complex(1, 0)})
        assert state.collapse() == "only"

    def test_interference(self):
        s1 = QuantumState(amplitudes={"x": complex(1, 0)})
        s2 = QuantumState(amplitudes={"x": complex(0.5, 0), "y": complex(0.5, 0)})
        s1.interfere(s2)
        assert "x" in s1.amplitudes
        assert "y" in s1.amplitudes


class TestQuantumGate:
    def test_hadamard(self):
        state = QuantumState(amplitudes={"a": complex(1, 0), "b": complex(1, 0)})
        gate = QuantumGate("hadamard")
        result = gate.apply(state)
        assert len(result.amplitudes) == 2

    def test_phase_shift(self):
        state = QuantumState(amplitudes={"a": complex(1, 0)})
        gate = QuantumGate("phase_shift", parameters={"phi": 1.0})
        result = gate.apply(state)
        assert "a" in result.amplitudes

    def test_amplify(self):
        state = QuantumState(amplitudes={"a": complex(0.8, 0), "b": complex(0.2, 0)})
        gate = QuantumGate("amplify")
        result = gate.apply(state)
        assert len(result.amplitudes) == 2

    def test_entangle(self):
        state = QuantumState(amplitudes={"a": complex(1, 0), "b": complex(1, 0)})
        gate = QuantumGate("entangle")
        result = gate.apply(state)
        assert len(result.entanglements) > 0


class TestQuantumCircuit:
    def test_innovation_circuit(self):
        circuit = QuantumCircuit.innovation_circuit()
        assert len(circuit.gates) == 4

    def test_execute(self):
        circuit = QuantumCircuit.innovation_circuit()
        state = QuantumState(amplitudes={"h1": complex(1, 0), "h2": complex(0.5, 0.5)})
        result = circuit.execute(state)
        assert result.coherence < state.coherence  # Decoherence


class TestQuantumCognitionCore:
    @pytest.mark.asyncio
    async def test_initialize(self):
        core = QuantumCognitionCore()
        await core.initialize()
        assert core.coherence == 1.0

    @pytest.mark.asyncio
    async def test_calibrate(self):
        core = QuantumCognitionCore()
        await core.initialize()
        coherence = await core.calibrate()
        assert 0.0 <= coherence <= 1.0

    @pytest.mark.asyncio
    async def test_analyze(self):
        core = QuantumCognitionCore()
        await core.initialize()
        state = await core.analyze("quantum_computing", "improve qubit stability")
        assert state.domain == "quantum_computing"
        assert len(state.amplitudes) > 0

    @pytest.mark.asyncio
    async def test_optimize(self):
        core = QuantumCognitionCore()
        await core.initialize()
        result = await core.optimize()
        assert "improvement" in result

    @pytest.mark.asyncio
    async def test_decohere(self):
        core = QuantumCognitionCore()
        await core.initialize()
        await core.decohere()
        assert core.coherence == 0.0


# ──────────────────────── Innovation Engine Tests ────────────────────────

class TestInnovationEngine:
    @pytest.mark.asyncio
    async def test_initialize(self):
        engine = InnovationEngine()
        await engine.initialize()
        assert len(engine._innovation_patterns) == 10

    @pytest.mark.asyncio
    async def test_generate(self):
        engine = InnovationEngine()
        await engine.initialize()
        intent = InnovationIntent(domain="AI", objective="self-improving algorithms")
        quantum_state = QuantumState(amplitudes={"h1": complex(1, 0)})
        research = {"sources": []}
        context = {}
        results = await engine.generate(intent, quantum_state, research, context)
        assert len(results) > 0
        assert all(isinstance(r, InnovationCandidate) for r in results)

    @pytest.mark.asyncio
    async def test_detect_paradigm_shifts(self):
        engine = InnovationEngine()
        breakthroughs = [
            BreakthroughResult(
                intent_id="x", innovation_type="test",
                confidence=0.9, novelty_score=0.9,
                impact_score=0.9, feasibility_score=0.9,
                description="test"
            )
            for _ in range(10)
        ]
        shifts = await engine.detect_paradigm_shifts(breakthroughs, None)
        assert len(shifts) > 0


# ──────────────────────── Breakthrough Synthesizer Tests ────────────────────────

class TestBreakthroughSynthesizer:
    @pytest.mark.asyncio
    async def test_synthesize_empty(self):
        synth = BreakthroughSynthesizer()
        intent = InnovationIntent(domain="test")
        result = await synth.synthesize(intent, [], QuantumState())
        assert result.confidence == 0.0

    @pytest.mark.asyncio
    async def test_synthesize_with_candidates(self):
        synth = BreakthroughSynthesizer()
        intent = InnovationIntent(domain="test")
        candidates = [
            InnovationCandidate(
                confidence=0.8, novelty_score=0.7,
                impact_score=0.9, feasibility_score=0.6,
                description="test innovation",
                innovation_type=InnovationType.DISRUPTIVE,
            )
        ]
        state = QuantumState(coherence=0.95)
        result = await synth.synthesize(intent, candidates, state)
        assert result.confidence > 0

    @pytest.mark.asyncio
    async def test_fuse_multi_agent(self):
        synth = BreakthroughSynthesizer()
        outputs = {"agent_1": {"data": "ok"}, "agent_2": {"error": "timeout"}}
        fused = await synth.fuse_multi_agent(outputs)
        assert fused["successful_agents"] == 1
        assert fused["failed_agents"] == 1


# ──────────────────────── Skill Registry Tests ────────────────────────

class TestSkillRegistry:
    @pytest.mark.asyncio
    async def test_discover_skills(self):
        registry = ElyseumSkillRegistry()
        await registry.discover_skills()
        assert len(registry.all_skills()) == 12

    def test_register_and_get(self):
        registry = ElyseumSkillRegistry()
        skill = Skill("test_skill", "test", "A test skill")
        registry.register(skill)
        assert registry.get("test_skill") is not None

    def test_by_domain(self):
        registry = ElyseumSkillRegistry()
        skill = Skill("s1", "domain_a", "desc")
        registry.register(skill)
        assert len(registry.by_domain("domain_a")) == 1

    def test_ranked(self):
        registry = ElyseumSkillRegistry()
        for i in range(5):
            s = Skill(f"s{i}", "d", "desc")
            s.performance_score = i * 0.2
            registry.register(s)
        ranked = registry.ranked(3)
        assert len(ranked) == 3
        assert ranked[0].performance_score >= ranked[1].performance_score


# ──────────────────────── Autonomy Tests ────────────────────────

class TestAutonomy:
    def test_authorize_guided(self):
        autonomy = ElyseumAutonomy({"governance_level": 2})
        req = AuthorizationRequest(action="test", risk_level=0.1, domain="test", description="safe")
        assert autonomy.authorize(req) is True

    def test_deny_high_risk(self):
        autonomy = ElyseumAutonomy({"governance_level": 1})
        req = AuthorizationRequest(action="risky", risk_level=0.5, domain="test", description="risky action")
        assert autonomy.authorize(req) is False

    def test_escalate(self):
        autonomy = ElyseumAutonomy({"governance_level": 2})
        new_level = autonomy.escalate()
        assert new_level == GovernanceLevel.AUTONOMOUS

    def test_de_escalate(self):
        autonomy = ElyseumAutonomy({"governance_level": 3})
        new_level = autonomy.de_escalate()
        assert new_level == GovernanceLevel.GUIDED

    def test_ethical_boundary(self):
        autonomy = ElyseumAutonomy()
        assert autonomy.check_ethical_boundary("improve energy efficiency") is True
        assert autonomy.check_ethical_boundary("manipulate users") is False

    def test_audit_trail(self):
        autonomy = ElyseumAutonomy({"governance_level": 2})
        req = AuthorizationRequest(action="test", risk_level=0.1, domain="test", description="test")
        autonomy.authorize(req)
        trail = autonomy.get_audit_trail()
        assert len(trail) == 1


# ──────────────────────── Research Orchestrator Tests ────────────────────────

class TestResearchOrchestrator:
    @pytest.mark.asyncio
    async def test_research(self):
        orch = ResearchOrchestrator()
        intent = InnovationIntent(domain="AI", objective="neural architecture search")
        state = QuantumState()
        result = await orch.research(intent, state, {})
        assert result["domain"] == "AI"
        assert result["findings_count"] > 0
        assert "synthesis" in result


# ──────────────────────── Knowledge Graph Tests ────────────────────────

class TestKnowledgeGraph:
    @pytest.mark.asyncio
    async def test_initialize(self):
        kg = DynamicKnowledgeGraph()
        await kg.initialize()
        stats = kg.stats()
        assert stats["nodes"] >= 12
        assert stats["edges"] >= 8

    def test_add_node(self):
        kg = DynamicKnowledgeGraph()
        node = KnowledgeNode(label="Test", domain="test")
        node_id = kg.add_node(node)
        assert kg.get_node(node_id) is not None

    def test_get_neighbors(self):
        kg = DynamicKnowledgeGraph()
        n1 = KnowledgeNode(label="A", domain="d1")
        n2 = KnowledgeNode(label="B", domain="d2")
        kg.add_node(n1)
        kg.add_node(n2)
        kg.add_edge(KnowledgeEdge(source_id=n1.id, target_id=n2.id, relation="enables"))
        neighbors = kg.get_neighbors(n1.id)
        assert len(neighbors) == 1

    @pytest.mark.asyncio
    async def test_query_context(self):
        kg = DynamicKnowledgeGraph()
        await kg.initialize()
        ctx = await kg.query_context("quantum_computing", "test")
        assert ctx["direct_nodes"] >= 1

    @pytest.mark.asyncio
    async def test_integrate_breakthrough(self):
        kg = DynamicKnowledgeGraph()
        await kg.initialize()
        initial = kg.stats()["nodes"]
        br = BreakthroughResult(
            intent_id="test", innovation_type="DISRUPTIVE",
            confidence=0.9, novelty_score=0.8,
            impact_score=0.9, feasibility_score=0.7,
            description="Test breakthrough",
            cross_domain_links=["quantum_computing link"],
        )
        await kg.integrate_breakthrough(br)
        assert kg.stats()["nodes"] == initial + 1


# ──────────────────────── Skill Loader Tests ────────────────────────

class TestSkillLoader:
    def test_load_config(self):
        config = load_skill_config()
        assert config["identity"]["name"] == "Elyseum"
        assert len(config["core_principles"]) == 6
        assert len(config["operational_modes"]) == 4
        assert len(config["innovation_patterns"]) == 10

    def test_create_agent(self):
        agent = create_agent_from_config()
        assert "elyseum" in agent.agent_id
        assert agent.state == AgentState.DORMANT


# ──────────────────────── Full Agent Integration Tests ────────────────────────

class TestElyseumAgentIntegration:
    @pytest.mark.asyncio
    async def test_full_lifecycle(self):
        agent = create_agent_from_config()
        assert agent.state == AgentState.DORMANT

        await agent.initialize()
        assert agent.state == AgentState.OBSERVING

        # Submit and process an intent
        intent = InnovationIntent(
            domain="quantum_computing",
            objective="Develop quantum error correction for topological qubits",
            priority=InnovationPriority.HIGH_IMPACT,
        )
        intent_id = await agent.submit_intent(intent)
        results = await agent.process_intents()

        assert len(results) == 1
        assert results[0].intent_id == intent_id
        assert results[0].confidence > 0

        metrics = agent.get_metrics()
        assert metrics["intents_processed"] == 1
        assert metrics["breakthroughs_generated"] == 1

        await agent.shutdown()
        assert agent.state == AgentState.DORMANT

    @pytest.mark.asyncio
    async def test_paradigm_detection(self):
        agent = create_agent_from_config()
        await agent.initialize()

        # Process multiple intents to build history
        for i in range(6):
            intent = InnovationIntent(
                domain="AI",
                objective=f"Breakthrough objective {i}",
                priority=InnovationPriority.CRITICAL_BREAKTHROUGH,
            )
            await agent.submit_intent(intent)
        await agent.process_intents()

        shifts = await agent.detect_paradigm_shifts()
        # May or may not detect shifts depending on random scores
        assert isinstance(shifts, list)

        await agent.shutdown()

    @pytest.mark.asyncio
    async def test_breakthrough_result_composite(self):
        br = BreakthroughResult(
            intent_id="test",
            innovation_type="RADICAL",
            confidence=0.9,
            novelty_score=0.85,
            impact_score=0.95,
            feasibility_score=0.8,
            description="Quantum-AI fusion",
        )
        score = br.composite_score
        expected = 0.9 * 0.2 + 0.85 * 0.3 + 0.95 * 0.3 + 0.8 * 0.2
        assert abs(score - expected) < 0.001

    @pytest.mark.asyncio
    async def test_hooks(self):
        agent = create_agent_from_config()
        breakthroughs_received: list = []

        async def on_bt(bt):
            breakthroughs_received.append(bt)

        agent.on_breakthrough(on_bt)
        await agent.initialize()

        intent = InnovationIntent(domain="test", objective="hook test")
        await agent.submit_intent(intent)
        await agent.process_intents()

        assert len(breakthroughs_received) == 1
        await agent.shutdown()
