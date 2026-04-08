"""Tests for Event Bus."""
import pytest
import asyncio
from src.core.event_bus import EventBus, Event, EventType

@pytest.mark.asyncio
async def test_subscribe_and_publish():
    bus = EventBus()
    received = []
    async def handler(event):
        received.append(event)
    bus.subscribe(EventType.INTENT_SUBMITTED, handler)
    await bus.publish(Event(event_type=EventType.INTENT_SUBMITTED, source="test"))
    assert len(received) == 1

@pytest.mark.asyncio
async def test_global_handler():
    bus = EventBus()
    received = []
    async def handler(event):
        received.append(event)
    bus.subscribe_all(handler)
    await bus.publish(Event(event_type=EventType.NODE_STARTED, source="test"))
    await bus.publish(Event(event_type=EventType.NODE_STOPPED, source="test"))
    assert len(received) == 2

@pytest.mark.asyncio
async def test_unsubscribe():
    bus = EventBus()
    received = []
    async def handler(event):
        received.append(event)
    bus.subscribe(EventType.HEALTH_CHECK, handler)
    bus.unsubscribe(EventType.HEALTH_CHECK, handler)
    await bus.publish(Event(event_type=EventType.HEALTH_CHECK, source="test"))
    assert len(received) == 0

@pytest.mark.asyncio
async def test_stats():
    bus = EventBus()
    s = bus.stats
    assert s["processed"] == 0
    assert s["errors"] == 0
