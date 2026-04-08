"""Tests for Collective Bargaining Engine."""
import pytest
from src.collective_bargaining.engine import CollectiveBargainingEngine

@pytest.fixture
def engine():
    return CollectiveBargainingEngine()

@pytest.mark.asyncio
async def test_create_cluster(engine):
    members = {f"pea-{i}" for i in range(15)}
    cluster = await engine.create_cluster("energy", members, "utility-co")
    assert cluster.size == 15
    assert cluster.is_viable is True
    assert cluster.bargaining_power > 0

@pytest.mark.asyncio
async def test_join_cluster(engine):
    members = {f"pea-{i}" for i in range(5)}
    cluster = await engine.create_cluster("energy", members, "utility-co", min_members=3)
    result = await engine.join_cluster(cluster.cluster_id, "pea-new")
    assert result is True
    assert cluster.size == 6

@pytest.mark.asyncio
async def test_negotiation_flow(engine):
    members = {f"pea-{i}" for i in range(20)}
    cluster = await engine.create_cluster("energy", members, "utility-co")
    assert await engine.start_negotiation(cluster.cluster_id) is True
    rnd = await engine.submit_round(cluster.cluster_id,
        {"price_per_kwh": 0.08}, approval_rate=0.75)
    assert rnd is not None
    assert rnd.accepted is True
    assert cluster.status == "settled"

@pytest.mark.asyncio
async def test_benefit_distribution(engine):
    members = {f"pea-{i}" for i in range(10)}
    cluster = await engine.create_cluster("energy", members, "uc", min_members=5)
    dist = await engine.calculate_benefit_distribution(cluster.cluster_id, 1000.0)
    assert len(dist) == 10
    assert abs(sum(dist.values()) - 1000.0) < 0.01

@pytest.mark.asyncio
async def test_nonviable_cluster(engine):
    members = {"pea-0", "pea-1"}
    cluster = await engine.create_cluster("energy", members, "uc", min_members=10)
    assert cluster.is_viable is False
    assert await engine.start_negotiation(cluster.cluster_id) is False
