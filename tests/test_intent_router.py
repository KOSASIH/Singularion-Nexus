"""Tests for Intent Router."""
import pytest
from src.intent_router.router import IntentRouter, ServiceRegistration

@pytest.fixture
def router():
    r = IntentRouter()
    for i in range(3):
        r.register_service(ServiceRegistration(
            provider_id=f"provider-{i}", domain="energy",
            capabilities=["supply"], pricing={"base": 50 + i * 10},
            quality_score=0.9 - i * 0.1))
    return r

@pytest.mark.asyncio
async def test_find_paths(router):
    paths = await router.find_paths("intent-1", "energy", {})
    assert len(paths) == 3

@pytest.mark.asyncio
async def test_select_optimal(router):
    paths = await router.find_paths("intent-1", "energy", {})
    decision = await router.select_optimal_path("intent-1", paths)
    assert decision.selected_path is not None
    assert decision.confidence > 0

@pytest.mark.asyncio
async def test_no_paths_raises(router):
    with pytest.raises(ValueError):
        await router.select_optimal_path("intent-x", [])

@pytest.mark.asyncio
async def test_execute_fulfillment(router):
    paths = await router.find_paths("i1", "energy", {})
    decision = await router.select_optimal_path("i1", paths)
    result = await router.execute_fulfillment(decision)
    assert result["status"] == "executing"
