"""Tests for PEA Mesh Protocol."""
import pytest
from src.pea_mesh.protocol import MeshProtocol, MeshMessage, MessageType

@pytest.fixture
def mesh():
    return MeshProtocol(node_id="test-node", listen_port=19999)

@pytest.mark.asyncio
async def test_connect_peer(mesh):
    peer = await mesh.connect_peer("127.0.0.1", 9091)
    assert peer is not None
    assert peer.peer_id in mesh.peers

@pytest.mark.asyncio
async def test_broadcast(mesh):
    await mesh.connect_peer("127.0.0.1", 9091)
    await mesh.connect_peer("127.0.0.1", 9092)
    msg = MeshMessage(message_id="m1", message_type=MessageType.INTENT_BROADCAST,
                      sender_id="other", payload={"intent": "test"})
    sent = await mesh.broadcast(msg)
    assert sent == 2

@pytest.mark.asyncio
async def test_duplicate_filter(mesh):
    await mesh.connect_peer("127.0.0.1", 9091)
    msg = MeshMessage(message_id="dup", message_type=MessageType.STATE_SYNC,
                      sender_id="other", payload={})
    first = await mesh.broadcast(msg)
    second = await mesh.broadcast(msg)
    assert first == 1
    assert second == 0

@pytest.mark.asyncio
async def test_handler_registration(mesh):
    called = []
    mesh.on_message(MessageType.HEARTBEAT, lambda m: called.append(m))
    assert MessageType.HEARTBEAT in mesh._message_handlers

def test_message_serialization():
    msg = MeshMessage(message_id="ser1", message_type=MessageType.INTENT_BROADCAST,
                      sender_id="node1", payload={"key": "value"})
    data = msg.serialize()
    assert len(data) > 4
    # Deserialize (skip 4-byte length header)
    restored = MeshMessage.deserialize(data[4:])
    assert restored.message_id == "ser1"
    assert restored.payload["key"] == "value"
