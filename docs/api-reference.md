# API Reference

REST, WebSocket, and gRPC interfaces.

---

## REST API — port 8080

Base: `http://localhost:8080/api/v1`

### Intents
```
POST   /intents          Submit intent
GET    /intents/{id}     Status
DELETE /intents/{id}     Cancel
GET    /intents          List active
```

**Submit Intent**
```json
{
  "type": "financial",
  "domain": "financial",
  "action": "optimize_portfolio",
  "constraints": {"risk_tolerance": 0.5, "budget": 50000},
  "priority": 8
}
```
**Response**
```json
{
  "intent_id": "intent-abc123",
  "status": "routing",
  "coalition_id": "coalition-xyz",
  "estimated_completion_ms": 1500
}
```

### Agents
```
GET  /agents             List (paginated)
GET  /agents/{id}        Profile
GET  /agents/{id}/status Live status
GET  /agents/domain/{d}  By domain
```

### Coalitions
```
POST   /coalitions       Form
GET    /coalitions        List
GET    /coalitions/{id}  Details
DELETE /coalitions/{id}  Dissolve
```

### Mesh
```
GET  /mesh/status        Health
GET  /mesh/topology      Network graph
GET  /mesh/metrics       Prometheus
POST /mesh/evolve        Trigger evolution (Kaelix)
```

---

## WebSocket — ws://localhost:8080/ws

```javascript
const ws = new WebSocket("ws://localhost:8080/ws");
ws.send(JSON.stringify({action:"subscribe", topic:"intents"}));
ws.onmessage = e => console.log(JSON.parse(e.data));
```

**Events**: `intent_received`, `coalition_formed`, `intent_completed`,
`agent_status`, `threat_detected`, `nous_awakened`

---

## gRPC — port 9090

```protobuf
service NexusMesh {
  rpc SubmitIntent(IntentRequest) returns (IntentResponse);
  rpc StreamEvents(StreamRequest) returns (stream Event);
  rpc RegisterAgent(AgentManifest) returns (RegistrationResponse);
}
```

---

## Auth
```bash
# Get JWT
curl -X POST /api/v1/auth/token -d '{"did":"did:nexus:...","signature":"..."}'
# Use JWT
curl -H "Authorization: Bearer <token>" /api/v1/agents
```
