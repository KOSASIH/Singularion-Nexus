# Deployment Guide

---

## Docker Compose (Development)

```bash
docker-compose up --build
```

Services: nexus-node (8080), redis (6379), prometheus (9090), grafana (3000)

---

## Kubernetes (Production)

```bash
kubectl apply -f k8s/
# Or: helm install singularion-nexus ./charts/singularion-nexus
```

Resource requirements per node:
- Nexus Core: 4 CPU, 8GB RAM
- Agent Runtime: 2 CPU, 4GB RAM
- Quantum Fabric: 8 CPU, 16GB RAM

---

## Configuration (`configs/production.yaml`)

```yaml
mesh:
  node_id: ${NEXUS_NODE_ID}
  mesh_port: 9090
  api_port: 8080
  max_peers: 1024
  quantum_backend: ibm_quantum

coalition:
  max_size: 12
  consensus_threshold: 0.67

security:
  zkp_proving_system: groth16
  encryption: kyber-1024
  threat_monitoring: true

agents:
  tier_omega_enabled: true
  reputation_decay_rate: 0.001
```

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXUS_NODE_ID` | Node identifier | auto |
| `NEXUS_MESH_PORT` | P2P port | 9090 |
| `NEXUS_API_PORT` | REST port | 8080 |
| `QUANTUM_BACKEND` | Backend | simulator |
| `ZKP_SYSTEM` | ZKP system | groth16 |
| `LOG_LEVEL` | Log level | INFO |
| `REDIS_URL` | Redis URL | redis://localhost:6379 |

---

## Monitoring

Metrics at `/api/v1/mesh/metrics` (Prometheus format)

Key metrics:
- `nexus_intents_total` — total intents processed
- `nexus_coalitions_active` — currently active coalitions
- `nexus_agent_reputation{agent_id}` — agent reputation scores
- `nexus_quantum_circuit_executions_total` — quantum compute usage
- `nexus_threat_level` — current threat level (0=green, 3=black)
