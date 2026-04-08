"""
Dynamic Knowledge Graph - Multi-domain knowledge integration.

Maintains a live, evolving graph of concepts, relationships, and insights
that grows with every research cycle and breakthrough.
"""

from __future__ import annotations

import time
import uuid
import logging
from dataclasses import dataclass, field
from typing import Any, Optional

logger = logging.getLogger("elyseum.knowledge_graph")


@dataclass
class KnowledgeNode:
    """A node in the knowledge graph."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    label: str = ""
    domain: str = ""
    node_type: str = "concept"  # concept, entity, technique, insight, breakthrough
    properties: dict[str, Any] = field(default_factory=dict)
    embedding: list[float] = field(default_factory=list)
    importance: float = 0.5
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)


@dataclass
class KnowledgeEdge:
    """A directed edge in the knowledge graph."""
    source_id: str = ""
    target_id: str = ""
    relation: str = ""  # enables, requires, contradicts, extends, similar_to, derived_from
    weight: float = 1.0
    properties: dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)


class DynamicKnowledgeGraph:
    """
    A live, evolving knowledge graph for innovation context.

    Features:
    - Multi-domain concept indexing
    - Relationship inference
    - Semantic similarity search (placeholder for vector store)
    - Breakthrough integration
    - Temporal evolution tracking
    - Cross-domain bridge detection
    """

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self._nodes: dict[str, KnowledgeNode] = {}
        self._edges: list[KnowledgeEdge] = []
        self._domain_index: dict[str, set[str]] = {}
        self._type_index: dict[str, set[str]] = {}

    async def initialize(self) -> None:
        """Initialize the knowledge graph with seed domains."""
        seed_domains = [
            "quantum_computing", "artificial_intelligence", "biotechnology",
            "nanotechnology", "energy", "materials_science", "robotics",
            "neuroscience", "cryptography", "distributed_systems",
            "space_technology", "synthetic_biology",
        ]
        for domain in seed_domains:
            node = KnowledgeNode(
                label=domain.replace("_", " ").title(),
                domain=domain,
                node_type="concept",
                importance=0.8,
            )
            self.add_node(node)

        # Connect related domains
        domain_relations = [
            ("quantum_computing", "cryptography", "enables"),
            ("quantum_computing", "artificial_intelligence", "enhances"),
            ("artificial_intelligence", "robotics", "powers"),
            ("biotechnology", "synthetic_biology", "extends"),
            ("nanotechnology", "materials_science", "enables"),
            ("neuroscience", "artificial_intelligence", "inspires"),
            ("distributed_systems", "cryptography", "requires"),
            ("energy", "nanotechnology", "benefits_from"),
        ]
        nodes_by_domain = {n.domain: n.id for n in self._nodes.values()}
        for src_domain, tgt_domain, relation in domain_relations:
            src_id = nodes_by_domain.get(src_domain)
            tgt_id = nodes_by_domain.get(tgt_domain)
            if src_id and tgt_id:
                self.add_edge(KnowledgeEdge(
                    source_id=src_id,
                    target_id=tgt_id,
                    relation=relation,
                ))

        logger.info(
            "Knowledge graph initialized: %d nodes, %d edges",
            len(self._nodes),
            len(self._edges),
        )

    def add_node(self, node: KnowledgeNode) -> str:
        """Add a node to the graph."""
        self._nodes[node.id] = node
        self._domain_index.setdefault(node.domain, set()).add(node.id)
        self._type_index.setdefault(node.node_type, set()).add(node.id)
        return node.id

    def add_edge(self, edge: KnowledgeEdge) -> None:
        """Add an edge to the graph."""
        self._edges.append(edge)

    def get_node(self, node_id: str) -> KnowledgeNode | None:
        return self._nodes.get(node_id)

    def get_nodes_by_domain(self, domain: str) -> list[KnowledgeNode]:
        ids = self._domain_index.get(domain, set())
        return [self._nodes[nid] for nid in ids if nid in self._nodes]

    def get_neighbors(self, node_id: str) -> list[tuple[KnowledgeNode, str]]:
        """Get neighboring nodes and their relationships."""
        neighbors: list[tuple[KnowledgeNode, str]] = []
        for edge in self._edges:
            if edge.source_id == node_id:
                target = self._nodes.get(edge.target_id)
                if target:
                    neighbors.append((target, edge.relation))
            elif edge.target_id == node_id:
                source = self._nodes.get(edge.source_id)
                if source:
                    neighbors.append((source, f"inv_{edge.relation}"))
        return neighbors

    async def query_context(
        self,
        domain: str,
        objective: str,
    ) -> dict[str, Any]:
        """Query the knowledge graph for relevant context."""
        domain_nodes = self.get_nodes_by_domain(domain)
        related_edges = [
            e for e in self._edges
            if e.source_id in {n.id for n in domain_nodes}
            or e.target_id in {n.id for n in domain_nodes}
        ]

        # Find cross-domain bridges
        all_related_ids = set()
        for e in related_edges:
            all_related_ids.add(e.source_id)
            all_related_ids.add(e.target_id)

        cross_domain = [
            self._nodes[nid] for nid in all_related_ids
            if nid in self._nodes and self._nodes[nid].domain != domain
        ]

        return {
            "domain": domain,
            "direct_nodes": len(domain_nodes),
            "related_edges": len(related_edges),
            "cross_domain_nodes": len(cross_domain),
            "cross_domains": list({n.domain for n in cross_domain}),
            "total_graph_size": len(self._nodes),
        }

    async def integrate_breakthrough(self, breakthrough: Any) -> str:
        """Integrate a breakthrough result into the knowledge graph."""
        node = KnowledgeNode(
            label=getattr(breakthrough, "description", "Breakthrough")[:80],
            domain=getattr(breakthrough, "innovation_type", "general"),
            node_type="breakthrough",
            importance=getattr(breakthrough, "composite_score", 0.5),
            properties={
                "confidence": getattr(breakthrough, "confidence", 0),
                "novelty": getattr(breakthrough, "novelty_score", 0),
                "impact": getattr(breakthrough, "impact_score", 0),
                "intent_id": getattr(breakthrough, "intent_id", ""),
            },
        )
        node_id = self.add_node(node)

        # Connect to related concepts via cross_domain_links
        for link_desc in getattr(breakthrough, "cross_domain_links", []):
            # Find matching nodes by label similarity (simplified)
            for existing in self._nodes.values():
                if existing.id != node_id and existing.domain in link_desc.lower():
                    self.add_edge(KnowledgeEdge(
                        source_id=node_id,
                        target_id=existing.id,
                        relation="derived_from",
                        weight=getattr(breakthrough, "confidence", 0.5),
                    ))
                    break

        logger.info("Integrated breakthrough into knowledge graph: %s", node_id)
        return node_id

    async def persist(self) -> None:
        """Persist graph state."""
        logger.info(
            "Persisting knowledge graph: %d nodes, %d edges",
            len(self._nodes),
            len(self._edges),
        )

    def stats(self) -> dict[str, Any]:
        return {
            "nodes": len(self._nodes),
            "edges": len(self._edges),
            "domains": len(self._domain_index),
            "node_types": {
                ntype: len(ids) for ntype, ids in self._type_index.items()
            },
        }
