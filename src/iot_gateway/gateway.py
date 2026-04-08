"""IoT & Biometric Gateway.

Integrates biometric wearables and IoT devices for seamless,
invisible economic transactions.
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class DeviceType(Enum):
    WEARABLE = "wearable"
    SMART_HOME = "smart_home"
    SMART_METER = "smart_meter"
    VEHICLE = "vehicle"
    INDUSTRIAL = "industrial"


class AuthMethod(Enum):
    HEARTBEAT_PATTERN = "heartbeat_pattern"
    GAIT_ANALYSIS = "gait_analysis"
    VOICE_PRINT = "voice_print"
    BEHAVIORAL = "behavioral"
    MULTI_FACTOR = "multi_factor"


@dataclass
class IoTDevice:
    device_id: str
    device_type: DeviceType
    owner_pea_id: str
    capabilities: List[str] = field(default_factory=list)
    auth_method: AuthMethod = AuthMethod.MULTI_FACTOR
    status: str = "active"


@dataclass
class BiometricSignal:
    signal_id: str
    device_id: str
    auth_method: AuthMethod
    confidence: float
    signal_hash: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class IoTGateway:
    def __init__(self, gateway_port: int = 8883):
        self.gateway_port = gateway_port
        self.devices: Dict[str, IoTDevice] = {}
        self.auth_sessions: Dict[str, datetime] = {}

    async def register_device(self, device: IoTDevice) -> bool:
        self.devices[device.device_id] = device
        logger.info(f"Device registered: {device.device_id} ({device.device_type.value})")
        return True

    async def authenticate_biometric(self, signal: BiometricSignal, threshold: float = 0.95) -> bool:
        if signal.confidence < threshold:
            return False
        device = self.devices.get(signal.device_id)
        if not device:
            return False
        self.auth_sessions[device.owner_pea_id] = datetime.now(timezone.utc)
        return True

    async def trigger_invisible_transaction(self, pea_id: str, device_id: str, transaction_type: str, parameters: Dict[str, Any]) -> Optional[str]:
        if pea_id not in self.auth_sessions:
            return None
        device = self.devices.get(device_id)
        if not device or device.owner_pea_id != pea_id:
            return None
        logger.info(f"Invisible transaction: {transaction_type} via {device_id}")
        return f"txn-{pea_id[:8]}-{device_id[:8]}"
