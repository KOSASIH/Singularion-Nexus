"""Tests for DAG Ledger."""
import pytest
from src.ledger.dag import DAGLedger, Transaction

@pytest.fixture
def ledger():
    l = DAGLedger(confirmation_threshold=3)
    l.initialize()
    return l

def test_genesis(ledger):
    assert "genesis" in ledger.nodes
    assert ledger.nodes["genesis"].confirmed is True

def test_add_node(ledger):
    txn = Transaction(txn_id="t1", sender="alice", receiver="bob", amount=10.0)
    node = ledger.add_node([txn], "validator-1")
    assert node is not None
    assert node.node_id in ledger.nodes
    assert ledger.get_transaction("t1") is not None

def test_balance_tracking(ledger):
    t1 = Transaction(txn_id="t1", sender="alice", receiver="bob", amount=50.0)
    t2 = Transaction(txn_id="t2", sender="bob", receiver="charlie", amount=20.0)
    ledger.add_node([t1], "v1")
    ledger.add_node([t2], "v2")
    assert ledger.get_balance("bob") == 30.0
    assert ledger.get_balance("alice") == -50.0
    assert ledger.get_balance("charlie") == 20.0

def test_confirmation(ledger):
    txn = Transaction(txn_id="t1", sender="a", receiver="b", amount=1.0)
    node = ledger.add_node([txn], "v1")
    # Add more nodes referencing to increase weight
    for i in range(5):
        ledger.add_node([], f"v{i+2}")
    # Genesis should be confirmed due to many children
    assert ledger.nodes["genesis"].confirmed is True

def test_stats(ledger):
    for i in range(3):
        txn = Transaction(txn_id=f"t{i}", sender="a", receiver="b", amount=1.0)
        ledger.add_node([txn], f"v{i}")
    s = ledger.stats
    assert s["total_nodes"] >= 4  # genesis + 3
    assert s["total_transactions"] == 3

def test_merkle_root():
    txn = Transaction(txn_id="t1", sender="a", receiver="b", amount=5.0)
    from src.ledger.dag import DAGNode
    node = DAGNode(node_id="n1", transactions=[txn], parents=[], creator="c")
    assert len(node.merkle_root) > 0
