"""Hivemind — Sovereign of Collective Intelligence."""
from __future__ import annotations
import logging, uuid
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional
logger = logging.getLogger(__name__)

@dataclass
class SwarmTask:
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    objective: str = ""; subtasks: List[Dict]=field(default_factory=list)
    workers: List[str]=field(default_factory=list)
    results: List[Any]=field(default_factory=list); status: str="pending"

class Hivemind:
    """Orchestrates millions of sub-agents as unified cognitive superstructures."""
    def __init__(self, mesh=None):
        self.mesh=mesh; self._swarms: Dict[str,SwarmTask]={}; self._workers=0
        logger.info("Hivemind online")

    async def deploy_swarm(self, objective, agent_ids):
        task=SwarmTask(objective=objective, workers=agent_ids)
        n=max(len(agent_ids),1)
        for i,aid in enumerate(agent_ids):
            task.subtasks.append({"subtask_id":f"{task.task_id}-{i}","agent_id":aid,
                                   "slice":f"shard-{i+1}-of-{n}","objective":objective})
        task.status="running"; self._swarms[task.task_id]=task; self._workers+=len(agent_ids)
        logger.info(f"Swarm {task.task_id}: {len(agent_ids)} workers on '{objective}'"); return task

    async def synthesize(self, task_id, reducer=None):
        task=self._swarms.get(task_id)
        if not task: return None
        task.status="completed"
        return reducer(task.results) if reducer else {"synthesized":True,"count":len(task.results),"task_id":task_id}

    def status_report(self):
        return {"active":sum(1 for s in self._swarms.values() if s.status=="running"),
                "total_workers":self._workers,"total_tasks":len(self._swarms)}
