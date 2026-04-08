"""Test suite for ZKP Micro-Contract Engine."""

import pytest
import asyncio
from src.zkp_engine.contracts import ZKPEngine, ProofSystem, ContractStatus


@pytest.fixture
def zkp_engine():
    return ZKPEngine(default_system=ProofSystem.GROTH16)


@pytest.mark.asyncio
async def test_create_contract(zkp_engine):
    contract = await zkp_engine.create_contract(
        parties=["pea-alice", "pea-bob"],
        terms={"type": "energy_purchase", "amount_kwh": 100},
        domain="energy",
        value_range=(10.0, 50.0),
    )
    assert contract.contract_id
    assert contract.status == ContractStatus.DRAFT
    assert len(contract.parties) == 2


@pytest.mark.asyncio
async def test_generate_and_verify_proof(zkp_engine):
    contract = await zkp_engine.create_contract(
        parties=["pea-alice", "pea-bob"],
        terms={"type": "purchase"},
        domain="general",
    )
    proof = await zkp_engine.generate_proof(contract, {"secret": "value"})
    assert proof.proof_id
    assert proof.system == ProofSystem.GROTH16

    result = await zkp_engine.verify_proof(proof)
    assert result is True
    assert proof.verified is True


@pytest.mark.asyncio
async def test_settle_contract(zkp_engine):
    contract = await zkp_engine.create_contract(
        parties=["pea-1", "pea-2"],
        terms={"type": "settlement_test"},
        domain="finance",
    )
    proof = await zkp_engine.generate_proof(contract, {})
    await zkp_engine.verify_proof(proof)
    settled = await zkp_engine.settle_contract(contract.contract_id)
    assert settled is True
    assert contract.status == ContractStatus.SETTLED


@pytest.mark.asyncio
async def test_batch_verify(zkp_engine):
    contracts = []
    proofs = []
    for i in range(5):
        c = await zkp_engine.create_contract(
            parties=[f"pea-{i}a", f"pea-{i}b"],
            terms={"index": i},
            domain="test",
        )
        p = await zkp_engine.generate_proof(c, {})
        contracts.append(c)
        proofs.append(p)

    results = await zkp_engine.batch_verify(proofs)
    assert all(results)
    assert len(results) == 5
