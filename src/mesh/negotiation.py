"""Negotiation Engine. Protocols: one-shot, multi-round, Vickrey, Dutch."""
from __future__ import annotations
import logging, time, uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
logger = logging.getLogger(__name__)

class NegotiationProtocol(str, Enum):
    ONE_SHOT = "one_shot"; MULTI_ROUND = "multi_round"
    VICKREY = "vickrey"; DUTCH = "dutch"

class NegotiationStatus(str, Enum):
    OPEN = "open"; AGREED = "agreed"; FAILED = "failed"
    TIMEOUT = "timeout"; ESCALATED = "escalated"

@dataclass
class Offer:
    offer_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    from_agent: str = ""; terms: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

@dataclass
class NegotiationSession:
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    intent_id: str = ""; protocol: NegotiationProtocol = NegotiationProtocol.MULTI_ROUND
    parties: List[str] = field(default_factory=list); offers: List[Offer] = field(default_factory=list)
    status: NegotiationStatus = NegotiationStatus.OPEN; agreed_terms: Optional[Dict] = None
    rounds: int = 0; max_rounds: int = 10
    deadline: float = field(default_factory=lambda: time.time() + 30.0)
    def is_timed_out(self): return time.time() > self.deadline

class NegotiationEngine:
    def __init__(self, mesh, timeout=30.0):
        self.mesh = mesh; self.timeout = timeout; self._sessions: Dict[str, NegotiationSession] = {}

    async def open(self, intent_id, parties, initial_terms, protocol=NegotiationProtocol.MULTI_ROUND):
        s = NegotiationSession(intent_id=intent_id, protocol=protocol, parties=parties, deadline=time.time() + self.timeout)
        s.offers.append(Offer(from_agent=parties[0], terms=initial_terms))
        self._sessions[s.session_id] = s
        logger.info(f"Negotiation {s.session_id} opened ({len(parties)} parties)")
        return s

    async def submit_offer(self, session_id, from_agent, terms):
        s = self._sessions.get(session_id)
        if not s or s.status != NegotiationStatus.OPEN: return False
        if s.is_timed_out(): s.status = NegotiationStatus.TIMEOUT; return False
        s.offers.append(Offer(from_agent=from_agent, terms=terms)); s.rounds += 1
        if len(s.offers) >= 2:
            a, b = s.offers[-1].terms, s.offers[-2].terms
            agree = all(abs(a[k]-b[k])/abs(b[k]) <= 0.05 for k in a if k in b and isinstance(a[k],(int,float)) and isinstance(b[k],(int,float)) and b[k]!=0)
            if agree: s.status = NegotiationStatus.AGREED; s.agreed_terms = terms
        if s.rounds >= s.max_rounds and s.status == NegotiationStatus.OPEN: s.status = NegotiationStatus.FAILED
        return True

    async def escalate(self, session_id, to_agent="Arbiter"):
        s = self._sessions.get(session_id)
        if s: s.status = NegotiationStatus.ESCALATED; logger.info(f"Escalated {session_id} -> {to_agent}")

    def get(self, session_id): return self._sessions.get(session_id)
