"""Tests for Quantum LLM Engine."""
import pytest
import numpy as np
from src.quantum_llm.engine import (
    QuantumLLMEngine, QuantumBackend, QuantumStateVector, QuantumAttentionCircuit)

def test_state_vector_init():
    qsv = QuantumStateVector(2)
    assert qsv.dim == 4
    assert abs(qsv.state[0] - 1.0) < 1e-10

def test_hadamard():
    qsv = QuantumStateVector(1)
    qsv.hadamard(0)
    probs = qsv.probabilities
    assert abs(probs[0] - 0.5) < 1e-10
    assert abs(probs[1] - 0.5) < 1e-10

def test_measure():
    qsv = QuantumStateVector(2)
    qsv.hadamard(0)
    counts = qsv.measure(shots=1000)
    assert "00" in counts or "01" in counts or "10" in counts or "11" in counts
    assert sum(counts.values()) == 1000

def test_cnot():
    qsv = QuantumStateVector(2)
    qsv.hadamard(0)
    qsv.apply_cnot(0, 1)
    probs = qsv.probabilities
    # Bell state: |00> + |11> / sqrt(2)
    assert abs(probs[0] - 0.5) < 1e-10
    assert abs(probs[3] - 0.5) < 1e-10

def test_attention_circuit():
    attn = QuantumAttentionCircuit(n_qubits=3)
    q = np.array([0.5, 0.3, 0.7])
    k = np.array([0.2, 0.8, 0.4])
    weights = attn.compute_attention(q, k, shots=512)
    assert weights.shape[0] == 8
    assert abs(weights.sum() - 1.0) < 0.01

@pytest.mark.asyncio
async def test_parse_intent_energy():
    engine = QuantumLLMEngine(n_qubits=3)
    intent = await engine.parse_intent("I want to buy 100 kwh of solar energy")
    assert intent.domain == "energy"
    assert intent.action == "purchase"
    assert intent.confidence > 0.1

@pytest.mark.asyncio
async def test_parse_intent_travel():
    engine = QuantumLLMEngine(n_qubits=3)
    intent = await engine.parse_intent("Find the cheapest flight to NYC")
    assert intent.domain == "travel"
    assert intent.quantum_enhanced is True

@pytest.mark.asyncio
async def test_negotiation_strategy():
    engine = QuantumLLMEngine(n_qubits=3)
    from src.quantum_llm.engine import ParsedIntent
    intent = ParsedIntent(raw_text="negotiate energy", domain="energy", action="negotiate", confidence=0.9)
    strategy = await engine.generate_negotiation_strategy(
        intent, {"avg_price": 100.0}, ["provider1", "provider2"])
    assert strategy.opening_position["price"] < 100
    assert len(strategy.concession_curve) > 0
    assert strategy.quantum_advantage_score >= 0

@pytest.mark.asyncio
async def test_optimize_matching():
    engine = QuantumLLMEngine(n_qubits=3)
    demands = [{"max_price": 100, "quality": 0.8}, {"max_price": 50, "quality": 0.5}]
    offers = [{"price": 90, "quality": 0.7}, {"price": 45, "quality": 0.6}]
    matches = await engine.optimize_matching(demands, offers)
    assert len(matches) > 0
    for d_idx, o_idx, score in matches:
        assert score > 0
