"""PEA Mesh Protocol — Decentralized P2P mesh with TCP transport."""
from .protocol import MeshProtocol, MeshMessage, MessageType, PeerInfo
__all__ = ["MeshProtocol", "MeshMessage", "MessageType", "PeerInfo"]
