"""Tests for IoT Gateway."""
import pytest
from src.iot_gateway.gateway import IoTGateway, IoTDevice, BiometricSignal, DeviceType, AuthMethod

@pytest.fixture
def gateway():
    return IoTGateway(session_timeout_s=3600)

@pytest.fixture
def gateway_with_device(gateway):
    import asyncio
    device = IoTDevice(device_id="watch-1", device_type=DeviceType.WEARABLE,
                       owner_pea_id="pea-alice", capabilities=["heartbeat", "steps"])
    asyncio.get_event_loop().run_until_complete(gateway.register_device(device))
    return gateway

@pytest.mark.asyncio
async def test_register_device(gateway):
    device = IoTDevice(device_id="d1", device_type=DeviceType.SMART_HOME, owner_pea_id="pea-1")
    assert await gateway.register_device(device) is True
    assert len(gateway.devices) == 1

@pytest.mark.asyncio
async def test_biometric_auth(gateway):
    device = IoTDevice(device_id="watch-1", device_type=DeviceType.WEARABLE,
                       owner_pea_id="pea-alice")
    await gateway.register_device(device)
    signal = BiometricSignal(signal_id="s1", device_id="watch-1",
                             auth_method=AuthMethod.HEARTBEAT_PATTERN,
                             confidence=0.98, signal_hash="abc123")
    assert await gateway.authenticate_biometric(signal) is True
    assert "pea-alice" in gateway.auth_sessions

@pytest.mark.asyncio
async def test_biometric_auth_low_confidence(gateway):
    device = IoTDevice(device_id="watch-1", device_type=DeviceType.WEARABLE,
                       owner_pea_id="pea-alice")
    await gateway.register_device(device)
    signal = BiometricSignal(signal_id="s2", device_id="watch-1",
                             auth_method=AuthMethod.HEARTBEAT_PATTERN,
                             confidence=0.5, signal_hash="low")
    assert await gateway.authenticate_biometric(signal) is False

@pytest.mark.asyncio
async def test_invisible_transaction(gateway):
    device = IoTDevice(device_id="watch-1", device_type=DeviceType.WEARABLE,
                       owner_pea_id="pea-alice")
    await gateway.register_device(device)
    signal = BiometricSignal(signal_id="s3", device_id="watch-1",
                             auth_method=AuthMethod.HEARTBEAT_PATTERN,
                             confidence=0.99, signal_hash="ok")
    await gateway.authenticate_biometric(signal)
    txn_id = await gateway.trigger_invisible_transaction(
        "pea-alice", "watch-1", "payment", {"amount": 5.0})
    assert txn_id is not None
    assert gateway.stats["transactions"] == 1

@pytest.mark.asyncio
async def test_transaction_without_auth(gateway):
    device = IoTDevice(device_id="d1", device_type=DeviceType.WEARABLE, owner_pea_id="pea-1")
    await gateway.register_device(device)
    txn = await gateway.trigger_invisible_transaction("pea-1", "d1", "pay", {})
    assert txn is None
