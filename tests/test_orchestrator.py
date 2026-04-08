"""Test suite for Nexus Core Orchestrator."""

import pytest
from src.core.orchestrator import NexusOrchestrator, NexusConfig, Intent


@pytest.fixture
def orchestrator():
    config = NexusConfig(node_id="test-node", max_peers=10)
    return NexusOrchestrator(config)


@pytest.mark.asyncio
async def test_start_stop(orchestrator):
    await orchestrator.start()
    assert orchestrator._running is True
    await orchestrator.stop()
    assert orchestrator._running is False


@pytest.mark.asyncio
async def test_submit_intent(orchestrator):
    await orchestrator.start()
    intent = Intent(intent_id="test-1", pea_id="pea-alice", intent_type="negotiate", domain="energy")
    result = await orchestrator.submit_intent(intent)
    assert "routed" in result
    assert "test-1" in orchestrator.active_intents


@pytest.mark.asyncio
async def test_register_peer(orchestrator):
    result = await orchestrator.register_peer("peer-1", {"address": "127.0.0.1"})
    assert result is True
    assert "peer-1" in orchestrator.peer_registry


@pytest.mark.asyncio
async def test_max_peers_limit(orchestrator):
    for i in range(10):
        await orchestrator.register_peer(f"peer-{i}", {})
    result = await orchestrator.register_peer("peer-overflow", {})
    assert result is False
