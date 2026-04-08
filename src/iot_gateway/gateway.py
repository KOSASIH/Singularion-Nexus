"""IoT & Biometric Gateway — Device management, auth, invisible transactions."""

import hashlib
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone, timedelta

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
    firmware_version: str = "1.0.0"
    last_seen: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class BiometricSignal:
    signal_id: str
    device_id: str
    auth_method: AuthMethod
    confidence: float
    signal_hash: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class TransactionRecord:
    txn_id: str
    pea_id: str
    device_id: str
    transaction_type: str
    parameters: Dict[str, Any]
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = "completed"


class IoTGateway:
    def __init__(self, session_timeout_s: int = 3600):
        self.devices: Dict[str, IoTDevice] = {}
        self.auth_sessions: Dict[str, datetime] = {}
        self.transaction_log: List[TransactionRecord] = []
        self.session_timeout = timedelta(seconds=session_timeout_s)
        self._stats = {"auth_attempts": 0, "auth_success": 0, "transactions": 0}

    async def register_device(self, device: IoTDevice) -> bool:
        self.devices[device.device_id] = device
        logger.info(f"Device registered: {device.device_id} ({device.device_type.value})")
        return True

    async def authenticate_biometric(self, signal: BiometricSignal, threshold: float = 0.95) -> bool:
        self._stats["auth_attempts"] += 1
        if signal.confidence < threshold:
            return False
        device = self.devices.get(signal.device_id)
        if not device:
            return False
        self.auth_sessions[device.owner_pea_id] = datetime.now(timezone.utc)
        device.last_seen = datetime.now(timezone.utc)
        self._stats["auth_success"] += 1
        return True

    async def trigger_invisible_transaction(
        self, pea_id: str, device_id: str, transaction_type: str,
        parameters: Dict[str, Any],
    ) -> Optional[str]:
        # Check session validity
        session_time = self.auth_sessions.get(pea_id)
        if not session_time or datetime.now(timezone.utc) - session_time > self.session_timeout:
            return None
        device = self.devices.get(device_id)
        if not device or device.owner_pea_id != pea_id:
            return None
        txn_id = hashlib.sha256(
            f"{pea_id}:{device_id}:{transaction_type}:{datetime.now(timezone.utc).timestamp()}".encode()
        ).hexdigest()[:16]
        record = TransactionRecord(
            txn_id=txn_id, pea_id=pea_id, device_id=device_id,
            transaction_type=transaction_type, parameters=parameters)
        self.transaction_log.append(record)
        self._stats["transactions"] += 1
        return txn_id

    async def get_device_status(self, device_id: str) -> Optional[Dict[str, Any]]:
        device = self.devices.get(device_id)
        if not device:
            return None
        return {
            "device_id": device.device_id,
            "type": device.device_type.value,
            "status": device.status,
            "firmware": device.firmware_version,
            "last_seen": device.last_seen.isoformat(),
        }

    @property
    def stats(self) -> Dict[str, Any]:
        return {**self._stats, "devices": len(self.devices), "active_sessions": len(self.auth_sessions)}
