# Quickstart Guide

Get Singularion Nexus running in 5 minutes.

## Prerequisites
- Python 3.11+, Rust 1.75+, Docker & docker-compose, Git

## Install
```bash
git clone https://github.com/KOSASIH/Singularion-Nexus.git
cd Singularion-Nexus
pip install -e "[dev]"
```

## Run a Node
```python
import asyncio
from src.core.orchestrator import NexusOrchestrator, NexusConfig

async def main():
    async with NexusOrchestrator(NexusConfig(node_id="my-node", mesh_port=9090)) as nexus:
        result = await nexus.fulfill_intent({
            "domain": "financial", "action": "optimize_portfolio",
            "constraints": {"risk": 0.5, "horizon": "1y"},
        })
        print(result)

asyncio.run(main())
```

## Create a God-Level Agent
```python
from src.agents.base import GodLevelAgent, AgentTier, ExecutionResult

class MyAgent(GodLevelAgent):
    tier = AgentTier.BASE
    domain = "financial"
    skills = ["momentum_trading", "risk_parity"]

    async def execute(self, intent: dict) -> ExecutionResult:
        return ExecutionResult(
            agent_id=self.agent_id, intent_id=intent.get("intent_id", ""),
            status="success", output={"action": "buy", "symbol": "ETH", "qty": 10},
            quality_score=0.9,
        )
```

## Form a Coalition
```python
from src.mesh.coalition import CoalitionFormationEngine, CoalitionPattern

engine = CoalitionFormationEngine(mesh=nexus)
coalition = await engine.form(
    intent_id="i-001",
    requirements=[
        {"capability": "market_analysis"},
        {"capability": "risk_assessment"},
        {"capability": "trade_execution"},
    ],
    pattern=CoalitionPattern.AUCTION,
)
print(f"Lead: {coalition.lead.agent_id}, Size: {coalition.size}")
```

## Use Quantum Fabric
```python
from src.quantum.fabric import QuantumFabric, QuantumBackend

qf = QuantumFabric(backend=QuantumBackend.SIMULATOR)
# QAOA optimization
result = await qf.quantum_optimize([[0.5, 0.3], [0.3, 0.7]])
# Quantum key exchange
key, _ = await qf.quantum_key_exchange("peer-001")
# Entangle two agents
pair_id = await qf.entangle("agent-a", "agent-b")
```

## Dark Operations
```python
from src.security.dark_ops import DarkOpsLayer

ops = DarkOpsLayer(mesh=nexus)
# Encrypt
payload = ops.cipher_encrypt(b"sensitive_data", "did:nexus:recipient")
# Deterrence
await ops.basilisk_deter("hostile-actor", level=1.0)
```

## Docker
```bash
docker-compose up --build
# API: http://localhost:8080  |  Metrics: http://localhost:9090
```

## Tests
```bash
pytest tests/ -v
pytest tests/ --cov=src --cov-report=html
```
