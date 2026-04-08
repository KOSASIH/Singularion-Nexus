"""Tests for reputation system."""
import pytest
from src.core.reputation import ReputationEngine, ReputationEvent

@pytest.fixture
def engine():
    return ReputationEngine()

def test_default_trust(engine):
    assert engine.get_trust_score("unknown") == 0.5

def test_record_success(engine):
    ev = ReputationEvent(event_id="e1", subject_id="agent1", reporter_id="agent2",
                         event_type="transaction_success", score_delta=0.8)
    score = engine.record_event(ev)
    assert score > 0.4
    p = engine.get_or_create_profile("agent1")
    assert p.transaction_count == 1
    assert p.successful_transactions == 1

def test_record_failure(engine):
    ev = ReputationEvent(event_id="e2", subject_id="agent1", reporter_id="agent2",
                         event_type="transaction_fail", score_delta=0.2)
    engine.record_event(ev)
    p = engine.get_or_create_profile("agent1")
    assert p.transaction_count == 1
    assert p.successful_transactions == 0

def test_dispute_penalty(engine):
    for i in range(5):
        engine.record_event(ReputationEvent(
            event_id=f"s{i}", subject_id="a", reporter_id="b",
            event_type="transaction_success", score_delta=0.8))
    score_before = engine.get_trust_score("a")
    for i in range(3):
        engine.record_event(ReputationEvent(
            event_id=f"d{i}", subject_id="a", reporter_id="c",
            event_type="dispute", score_delta=0.1))
    score_after = engine.get_trust_score("a")
    assert score_after <= score_before

def test_is_trusted(engine):
    engine.record_event(ReputationEvent(
        event_id="e", subject_id="good", reporter_id="r",
        event_type="transaction_success", score_delta=0.9))
    assert engine.is_trusted("good") is True

def test_top_agents(engine):
    for i in range(5):
        engine.record_event(ReputationEvent(
            event_id=f"e{i}", subject_id=f"agent{i}", reporter_id="r",
            event_type="transaction_success", score_delta=0.5 + i*0.1))
    top = engine.get_top_agents(3)
    assert len(top) == 3
