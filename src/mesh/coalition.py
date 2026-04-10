"""Coalition Formation Engine v2. Patterns: Auction, Consensus, Pipeline, Swarm."""
from __future__ import annotations
import logging, uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
logger = logging.getLogger(__name__)

class CoalitionPattern(str, Enum):
    AUCTION = "auction"; CONSENSUS = "consensus"
    PIPELINE = "pipeline"; SWARM = "swarm"

class CoalitionRole(str, Enum):
    LEAD = "lead"; SUPPORT = "support"; VALIDATOR = "validator"
    GUARDIAN = "guardian"; TIMER = "timer"

@dataclass
class CoalitionMember:
    agent_id: str; role: CoalitionRole; domain: str; reputation: float
    skills: List[str] = field(default_factory=list)

@dataclass
class Coalition:
    coalition_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    intent_id: str = ""; pattern: CoalitionPattern = CoalitionPattern.AUCTION
    members: List[CoalitionMember] = field(default_factory=list)
    status: str = "forming"; result: Optional[Dict[str, Any]] = None

    @property
    def lead(self): return next((m for m in self.members if m.role == CoalitionRole.LEAD), None)
    @property
    def size(self): return len(self.members)

class CoalitionFormationEngine:
    """Forms optimal coalitions for incoming intents. Called by Kaelix."""
    def __init__(self, mesh, consensus_threshold=0.67, max_size=12):
        self.mesh = mesh; self.consensus_threshold = consensus_threshold
        self.max_size = max_size; self._active: Dict[str, Coalition] = {}

    async def form(self, intent_id, requirements, pattern=CoalitionPattern.AUCTION, preferred=None):
        fns = {CoalitionPattern.AUCTION: self._auction, CoalitionPattern.CONSENSUS: self._consensus,
               CoalitionPattern.PIPELINE: self._pipeline, CoalitionPattern.SWARM: self._swarm}
        c = await fns.get(pattern, self._auction)(intent_id, requirements, preferred if pattern in [CoalitionPattern.AUCTION, CoalitionPattern.CONSENSUS] else None)
        c.status = "active"; self._active[c.coalition_id] = c
        logger.info(f"Coalition {c.coalition_id}: {c.size} members ({pattern.value})")
        return c

    async def dissolve(self, cid, result=None):
        if cid in self._active:
            self._active[cid].status = "dissolved"; self._active[cid].result = result; del self._active[cid]

    async def _auction(self, intent_id, requirements, preferred):
        c = Coalition(intent_id=intent_id, pattern=CoalitionPattern.AUCTION)
        for i, req in enumerate(requirements):
            candidates = await self.mesh.get_agents_for_capability(req.get("capability", ""))
            if not candidates: continue
            best = max(candidates, key=lambda a: a.get("reputation", 0.5) * (1.2 if preferred and a["agent_id"] in preferred else 1.0))
            c.members.append(CoalitionMember(agent_id=best["agent_id"],
                role=CoalitionRole.LEAD if i == 0 else CoalitionRole.SUPPORT,
                domain=best.get("domain", ""), reputation=best.get("reputation", 0.5), skills=best.get("skills", [])))
        return c

    async def _consensus(self, intent_id, requirements, preferred):
        c = await self._auction(intent_id, requirements, preferred); c.pattern = CoalitionPattern.CONSENSUS; return c

    async def _pipeline(self, intent_id, requirements, preferred=None):
        c = Coalition(intent_id=intent_id, pattern=CoalitionPattern.PIPELINE)
        for i, req in enumerate(requirements):
            candidates = await self.mesh.get_agents_for_capability(req.get("capability", ""))
            if candidates:
                best = max(candidates, key=lambda a: a.get("reputation", 0))
                c.members.append(CoalitionMember(agent_id=best["agent_id"],
                    role=CoalitionRole.LEAD if i == 0 else CoalitionRole.SUPPORT,
                    domain=best.get("domain", ""), reputation=best.get("reputation", 0.5)))
        return c

    async def _swarm(self, intent_id, requirements, preferred=None):
        c = Coalition(intent_id=intent_id, pattern=CoalitionPattern.SWARM)
        for i, req in enumerate(requirements):
            for j, a in enumerate((await self.mesh.get_agents_for_capability(req.get("capability", "")))[:3]):
                c.members.append(CoalitionMember(agent_id=a["agent_id"],
                    role=CoalitionRole.LEAD if (i == 0 and j == 0) else CoalitionRole.SUPPORT,
                    domain=a.get("domain", ""), reputation=a.get("reputation", 0.5)))
                if c.size >= self.max_size: break
        return c
