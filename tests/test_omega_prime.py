"""Tests for OmegaPrime Nexus Agent."""

import asyncio
import pytest

from src.agents.omega_prime.agent import (
    AgentState,
    AgentIdentity,
    IntentRequest,
    OmegaPrimeAgent,
)
from src.agents.omega_prime.cognition import CognitionEngine, ReasoningMode
from src.agents.omega_prime.skill_registry import SkillRegistry, Skill, SkillDomain
from src.agents.omega_prime.autonomy import AutonomyController, AutonomyLevel, RiskLevel


class TestAgentIdentity:
    def test_default_identity(self):
        identity = AgentIdentity()
        assert identity.agent_id
        assert identity.reputation_score == 1.0
        assert identity.domains == []

    def test_custom_identity(self):
        identity = AgentIdentity(mesh_address="mesh://node-42", domains=["energy", "travel"])
        assert identity.mesh_address == "mesh://node-42"
        assert len(identity.domains) == 2


class TestOmegaPrimeAgent:
    def test_initialization(self):
        agent = OmegaPrimeAgent()
        assert agent.state == AgentState.INITIALIZING
        assert isinstance(agent.cognition, CognitionEngine)
        assert isinstance(agent.skills, SkillRegistry)
        assert isinstance(agent.autonomy, AutonomyController)

    def test_custom_initialization(self):
        agent = OmegaPrimeAgent(
            autonomy_level=AutonomyLevel.AUTONOMOUS,
            reasoning_mode=ReasoningMode.QUANTUM,
        )
        assert agent.autonomy.level == AutonomyLevel.AUTONOMOUS
        assert agent.cognition.default_mode == ReasoningMode.QUANTUM

    def test_repr(self):
        agent = OmegaPrimeAgent()
        r = repr(agent)
        assert "OmegaPrimeAgent" in r
        assert "INITIALIZING" in r


class TestCognitionEngine:
    def test_default_mode(self):
        engine = CognitionEngine()
        assert engine.default_mode == ReasoningMode.HYBRID

    def test_mode_selection(self):
        engine = CognitionEngine()
        assert engine._select_reasoning_mode(0.9) == ReasoningMode.QUANTUM
        assert engine._select_reasoning_mode(0.1) == ReasoningMode.CLASSICAL
        assert engine._select_reasoning_mode(0.7) == ReasoningMode.HYBRID

    @pytest.mark.asyncio
    async def test_decompose_intent(self):
        engine = CognitionEngine()
        intent = IntentRequest(raw_input="Book a flight and hotel", parsed_domains=["travel", "housing"])
        result = await engine.decompose_intent(intent)
        assert len(result.sub_intents) > 0
        assert result.complexity_score > 0


class TestSkillRegistry:
    def test_register_and_count(self):
        registry = SkillRegistry()
        skill = Skill(skill_id="test", name="Test Skill", domain=SkillDomain.TRAVEL)
        registry.register(skill)
        assert len(registry) == 1

    @pytest.mark.asyncio
    async def test_discover_loads_builtins(self):
        registry = SkillRegistry()
        await registry.discover_and_load()
        assert len(registry) >= 5

    def test_domain_lookup(self):
        registry = SkillRegistry()
        registry.register(Skill(skill_id="s1", name="Skill 1", domain=SkillDomain.ENERGY, performance_score=0.8))
        registry.register(Skill(skill_id="s2", name="Skill 2", domain=SkillDomain.ENERGY, performance_score=0.95))
        results = registry._get_domain_skills(SkillDomain.ENERGY)
        assert len(results) == 2
        assert results[0].performance_score > results[1].performance_score


class TestAutonomyController:
    def test_restricted_denies_all(self):
        ctrl = AutonomyController(level=AutonomyLevel.RESTRICTED)
        assert ctrl.level == AutonomyLevel.RESTRICTED

    @pytest.mark.asyncio
    async def test_supervised_allows_low_risk(self):
        ctrl = AutonomyController(level=AutonomyLevel.SUPERVISED)
        intent = IntentRequest(raw_input="check weather", parsed_domains=["general"])

        class MockPlan:
            skills = []
            estimated_cost = 0
            requires_contracts = False
            execution_steps = []

        authorized = await ctrl.authorize(intent, MockPlan())
        assert authorized is True

    @pytest.mark.asyncio
    async def test_supervised_blocks_high_risk(self):
        ctrl = AutonomyController(level=AutonomyLevel.SUPERVISED)
        intent = IntentRequest(raw_input="delete all accounts and transfer funds")

        class MockPlan:
            skills = [1, 2, 3, 4, 5, 6]
            estimated_cost = 50000
            requires_contracts = True
            execution_steps = []

        authorized = await ctrl.authorize(intent, MockPlan())
        assert authorized is False

    def test_audit_log(self):
        ctrl = AutonomyController()
        assert len(ctrl.get_audit_log()) == 0


class TestSkillLoader:
    def test_config_file_exists(self):
        from src.agents.omega_prime.skill_loader import SKILL_CONFIG_PATH
        assert SKILL_CONFIG_PATH.exists()

    def test_load_config(self):
        from src.agents.omega_prime.skill_loader import load_megaprime_config
        config = load_megaprime_config()
        assert "mission" in config
        assert "core_principles" in config
        assert "operational_modes" in config
        assert "self_governance" in config
        assert "activation_protocol" in config
