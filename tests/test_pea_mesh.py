"""Test suite for PEA Mesh Protocol."""

import pytest
import asyncio
from src.pea_mesh.protocol import MeshProtocol, MeshMessage, MessageType


@pytest.fixture
def mesh():
    return MeshProtocol(node_id="test-node", listen_port=9999)


@pytest.mark.asyncio
async def test_connect_peer(mesh):
    peer = await mesh.connect_peer("127.0.0.1", 9091)
    assert peer is not None
    assert peer.peer_id in mesh.peers


@pytest.mark.asyncio
async def test_broadcast(mesh):
    await mesh.connect_peer("127.0.0.1", 9091)
    await mesh.connect_peer("127.0.0.1", 9092)

    msg = MeshMessage(
        message_id="test-msg-1",
        message_type=MessageType.INTENT_BROADCAST,
        sender_id="other-node",
        payload={"intent": "test"},
    )
    sent = await mesh.broadcast(msg)
    assert sent == 2


@pytest.mark.asyncio
async def test_duplicate_message_filter(mesh):
    await mesh.connect_peer("127.0.0.1", 9091)

    msg = MeshMessage(
        message_id="dup-msg",
        message_type=MessageType.STATE_SYNC,
        sender_id="other",
        payload={},
    )
    first = await mesh.broadcast(msg)
    second = await mesh.broadcast(msg)
    assert first == 1
    assert second == 0


@pytest.mark.asyncio
async def test_message_handler_registration(mesh):
    called = []
    mesh.on_message(MessageType.HEARTBEAT, lambda m: called.append(m))
    assert MessageType.HEARTBEAT in mesh._message_handlers
