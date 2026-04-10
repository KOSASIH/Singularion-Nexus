"""Temporal Intelligence Engine. Aion (macro) + Kairos (micro)."""
from __future__ import annotations
import asyncio, logging, time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
logger = logging.getLogger(__name__)

@dataclass
class TemporalLock:
    lock_id: str; asset_id: str; unlock_at: float; owner_agent: str
    on_unlock: Optional[str]=None; metadata: Dict[str,Any]=field(default_factory=dict)
    @property
    def is_unlocked(self): return time.time()>=self.unlock_at
    @property
    def seconds_remaining(self): return max(0.0, self.unlock_at-time.time())

@dataclass
class ExecutionWindow:
    window_id: str; opens_at: float; closes_at: float
    quality_score: float; action_type: str; confidence: float=0.8
    @property
    def is_open(self): return self.opens_at<=time.time()<=self.closes_at

class TemporalEngine:
    """Aion + Kairos coordination for all time-sensitive mesh operations."""
    def __init__(self, mesh=None):
        self.mesh=mesh; self._locks: Dict[str,TemporalLock]={}; self._watch: Optional[asyncio.Task]=None

    async def start(self):
        self._watch=asyncio.create_task(self._loop()); logger.info("Temporal engine: Aion+Kairos online")
    async def stop(self):
        if self._watch: self._watch.cancel()

    async def create_lock(self, asset_id, unlock_at, owner_agent, on_unlock=None):
        lock=TemporalLock(f"lock-{asset_id}-{int(unlock_at)}", asset_id, unlock_at, owner_agent, on_unlock)
        self._locks[lock.lock_id]=lock; logger.info(f"Lock {lock.lock_id}: {lock.seconds_remaining:.0f}s"); return lock

    async def find_windows(self, action_type, horizon=3600.0, n=3):
        now=time.time()
        return [ExecutionWindow(f"w-{action_type}-{i}", now+(i+1)*(horizon/(n+1)),
                now+(i+1)*(horizon/(n+1))+300, 1.0-i*0.2, action_type) for i in range(n)]

    async def _loop(self):
        while True:
            try:
                await asyncio.sleep(1.0)
                for lid, lock in list(self._locks.items()):
                    if lock.is_unlocked and lock.on_unlock:
                        logger.info(f"Lock {lid} unlocked -> {lock.on_unlock}")
                        if self.mesh: await self.mesh.emit_intent({"type":lock.on_unlock,"lock_id":lid,"asset_id":lock.asset_id})
                        del self._locks[lid]
            except asyncio.CancelledError: break
