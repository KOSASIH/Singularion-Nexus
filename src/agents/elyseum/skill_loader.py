"""
Elyseum Skill Loader - Factory that loads YAML config and initializes the agent.
"""

from __future__ import annotations

import os
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger("elyseum.skill_loader")

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]


def load_skill_config(path: str | Path | None = None) -> dict[str, Any]:
    """Load the Elyseum skill YAML configuration."""
    if yaml is None:
        raise ImportError("PyYAML is required: pip install pyyaml")

    if path is None:
        path = Path(__file__).parent / "elyseum_skill.yaml"
    else:
        path = Path(path)

    with open(path, "r") as f:
        config = yaml.safe_load(f)

    logger.info("Loaded Elyseum skill config from %s", path)
    return config


def create_agent_from_config(
    config: dict[str, Any] | None = None,
    config_path: str | Path | None = None,
) -> "ElyseumAgent":
    """
    Factory: create a fully configured ElyseumAgent from YAML config.

    Usage:
        agent = create_agent_from_config()
        await agent.initialize()
    """
    from .agent import ElyseumAgent

    if config is None:
        config = load_skill_config(config_path)

    identity = config.get("identity", {})
    quantum_cfg = config.get("quantum_cognition", {}).get("parameters", {})
    governance_cfg = config.get("governance", {})
    evolution_cfg = config.get("evolution", {})

    agent_config = {
        "quantum": quantum_cfg,
        "innovation": {
            "ideation_count": 20,
            "top_candidates": 5,
        },
        "autonomy": {
            "governance_level": _resolve_governance_level(governance_cfg),
        },
        "knowledge_graph": config.get("knowledge_graph", {}),
    }

    agent = ElyseumAgent(
        agent_id=f"elyseum-{identity.get('codename', 'genesis').lower().replace(' ', '-')}",
        config=agent_config,
    )

    logger.info(
        "Created Elyseum agent: %s (codename: %s)",
        agent.agent_id,
        identity.get("codename", "unknown"),
    )
    return agent


def _resolve_governance_level(governance_cfg: dict[str, Any]) -> int:
    """Resolve governance level string to enum value."""
    level_map = {"restricted": 1, "guided": 2, "autonomous": 3, "sovereign": 4}
    default = governance_cfg.get("default_level", "guided")
    return level_map.get(default, 2)
