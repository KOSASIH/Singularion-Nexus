"""Tests for ZKP Micro-Contract Engine."""
import pytest
from src.zkp_engine.contracts import ZKPEngine, ProofSystem, ContractStatus

@pytest.fixture
def zkp():
    return ZKPEngine(default_system=ProofSystem.GROTH16)

@pytest.mark.asyncio
async def test_create_contract(zkp):
    c = await zkp.create_contract(
        parties=["alice", "bob"], terms={"type": "energy", "kwh": 100},
        domain="energy", value_range=(10.0, 50.0))
    assert c.contract_id
    assert c.status == ContractStatus.DRAFT
    assert len(c.parties) == 2
    assert len(c.merkle_root) > 0

@pytest.mark.asyncio
async def test_generate_and_verify_proof(zkp):
    c = await zkp.create_contract(parties=["a", "b"], terms={"type": "test"}, domain="general")
    proof = await zkp.generate_proof(c, {"secret": "value"})
    assert proof.proof_id
    assert proof.system == ProofSystem.GROTH16
    assert len(proof.proof_data) >= 96
    assert len(proof.commitment) == 32
    assert len(proof.challenge) == 32
    assert len(proof.response) == 32
    result = await zkp.verify_proof(proof)
    assert result is True
    assert proof.verified is True

@pytest.mark.asyncio
async def test_settle_contract(zkp):
    c = await zkp.create_contract(parties=["a", "b"], terms={"t": "settle"}, domain="finance")
    proof = await zkp.generate_proof(c, {})
    await zkp.verify_proof(proof)
    assert await zkp.settle_contract(c.contract_id) is True
    assert c.status == ContractStatus.SETTLED
    assert c.settled_at is not None

@pytest.mark.asyncio
async def test_settle_fails_without_proof(zkp):
    c = await zkp.create_contract(parties=["a"], terms={}, domain="test")
    assert await zkp.settle_contract(c.contract_id) is False

@pytest.mark.asyncio
async def test_batch_verify(zkp):
    proofs = []
    for i in range(5):
        c = await zkp.create_contract(parties=[f"a{i}", f"b{i}"], terms={"i": i}, domain="test")
        p = await zkp.generate_proof(c, {})
        proofs.append(p)
    results = await zkp.batch_verify(proofs)
    assert all(results)
    assert len(results) == 5
