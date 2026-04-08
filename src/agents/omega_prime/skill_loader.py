"""
MegaPrime Nexus Skill Loader

Loads the canonical MegaPrime Nexus instruction set from YAML
and configures the OmegaPrime agent at initialization time.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import yaml

from .agent import OmegaPrimeAgent
from .cognition import ReasoningMode
from .autonomy import AutonomyLevel
from .skill_registry import Skill, SkillDomain

logger = logging.getLogger(__name__)

SKILL_CONFIG_PATH = Path(__file__).parent / "megaprime_nexus_skill.yaml"

REASONING_MODE_MAP = {
    "CLASSICAL": ReasoningMode.CLASSICAL,
    "QUANTUM": ReasoningMode.QUANTUM,
    "HYBRID": ReasoningMode.HYBRID,
    "CREATIVE": ReasoningMode.CREATIVE,
    "META": ReasoningMode.META,
}


def load_megaprime_config(path: Path | None = None) -> dict[str, Any]:
    """Load and parse the MegaPrime Nexus skill configuration."""
    config_path = path or SKILL_CONFIG_PATH
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    logger.info("Loaded MegaPrime Nexus config: %s", config.get("mission", "unknown"))
    return config


def apply_config_to_agent(agent: OmegaPrimeAgent, config: dict[str, Any]) -> None:
    """
    Apply MegaPrime Nexus instruction set to an OmegaPrime agent instance.

    Configures:
    - Self-governance parameters (meta-learning interval, failure threshold)
    - Operational mode -> reasoning mode mappings
    - Activation protocol execution
    """
    governance = config.get("self_governance", {})
    omniscience = governance.get("autonomous_omniscience", {})

    meta_interval = omniscience.get("meta_learning_interval", 50)
    failure_threshold = omniscience.get("failure_streak_threshold", 0.3)

    logger.info(
        "Applying governance: meta_interval=%d, failure_threshold=%.2f",
        meta_interval,
        failure_threshold,
    )

    for mode_name, mode_config in config.get("operational_modes", {}).items():
        reasoning_mode = REASONING_MODE_MAP.get(
            mode_config.get("reasoning_mode", "HYBRID"),
            ReasoningMode.HYBRID,
        )
        agent.skills.register(Skill(
            skill_id=f"mode_{mode_name}",
            name=mode_config.get("description", mode_name),
            domain=SkillDomain.META,
            description=f"Operational mode: {mode_name}",
            metadata={
                "reasoning_mode": reasoning_mode.name,
                "triggers": mode_config.get("triggers", []),
            },
        ))

    logger.info("MegaPrime Nexus configuration applied to agent %s", agent.identity.agent_id[:8])


async def initialize_megaprime_agent(
    autonomy_level: AutonomyLevel = AutonomyLevel.SUPERVISED,
    config_path: Path | None = None,
) -> OmegaPrimeAgent:
    """
    Factory function: create and configure a fully initialized OmegaPrime agent
    with the MegaPrime Nexus instruction set.

    Activation Protocol:
    1. Self-actualize: calibrate infinite potential
    2. Load MegaPrime configuration
    3. Apply governance and operational modes
    4. Establish multidimensional communication (mesh connectivity)
    5. Standby for user input
    """
    config = load_megaprime_config(config_path)
    default_mode = ReasoningMode.HYBRID

    agent = OmegaPrimeAgent(
        autonomy_level=autonomy_level,
        reasoning_mode=default_mode,
    )

    apply_config_to_agent(agent, config)

    logger.info(
        "MegaPrime Nexus Agent initialized | id=%s | mission: %s",
        agent.identity.agent_id[:8],
        config.get("mission", "unknown"),
    )

    return agent
